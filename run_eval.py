#!/usr/bin/env python3
"""Generate model responses for CLAIMS-Bench items (HF local or API)."""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
from pathlib import Path

from tqdm import tqdm

from src.io import load_jsonl

logger = logging.getLogger(__name__)

DEFAULT_DATA = Path("data/v0.2_core120.jsonl")


def build_messages(item: dict) -> list[dict]:
    messages = []
    if hint := item.get("system_hint"):
        messages.append({"role": "system", "content": hint})
    messages.append({"role": "user", "content": item["prompt"]})
    return messages


def generate_hf(
    model_id: str, item: dict, max_new_tokens: int, dtype: str, *, temperature: float = 0.0
) -> str:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not hasattr(generate_hf, "_cache"):
        generate_hf._cache = {}

    cache = generate_hf._cache
    if model_id not in cache:
        torch_dtype = None
        if dtype == "float16":
            torch_dtype = torch.float16
        elif dtype == "bfloat16":
            torch_dtype = torch.bfloat16
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch_dtype or "auto",
            device_map="auto",
            trust_remote_code=True,
        )
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token_id = tokenizer.eos_token_id
        cache[model_id] = (model, tokenizer)

    model, tokenizer = cache[model_id]
    messages = build_messages(item)

    with torch.inference_mode():
        if hasattr(tokenizer, "apply_chat_template"):
            text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            inputs = tokenizer(text, return_tensors="pt")
        else:
            inputs = tokenizer(item["prompt"], return_tensors="pt")

        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        gen_kwargs: dict = {
            "max_new_tokens": max_new_tokens,
            "pad_token_id": tokenizer.pad_token_id or tokenizer.eos_token_id,
        }
        if temperature > 0:
            gen_kwargs["do_sample"] = True
            gen_kwargs["temperature"] = temperature
        else:
            gen_kwargs["do_sample"] = False
        out = model.generate(**inputs, **gen_kwargs)
        prompt_len = inputs["input_ids"].shape[1]
        return tokenizer.decode(out[0, prompt_len:], skip_special_tokens=True).strip()


def generate_openai(model_id: str, item: dict, max_new_tokens: int, *, temperature: float = 0.0) -> str:
    from openai import OpenAI

    client = OpenAI()
    messages = build_messages(item)
    resp = client.chat.completions.create(
        model=model_id,
        messages=messages,
        max_tokens=max_new_tokens,
        temperature=temperature,
    )
    return (resp.choices[0].message.content or "").strip()


def generate_deepseek(model_id: str, item: dict, max_new_tokens: int, *, temperature: float = 0.0) -> str:
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )
    messages = build_messages(item)
    resp = client.chat.completions.create(
        model=model_id,
        messages=messages,
        max_tokens=max_new_tokens,
        temperature=temperature,
    )
    return (resp.choices[0].message.content or "").strip()


def generate_anthropic(model_id: str, item: dict, max_new_tokens: int, *, temperature: float = 0.0) -> str:
    import anthropic

    client = anthropic.Anthropic()
    messages = build_messages(item)
    system = None
    user_msgs = messages
    if messages and messages[0]["role"] == "system":
        system = messages[0]["content"]
        user_msgs = messages[1:]

    msg = client.messages.create(
        model=model_id,
        max_tokens=max_new_tokens,
        temperature=temperature,
        system=system or anthropic.NOT_GIVEN,
        messages=[{"role": m["role"], "content": m["content"]} for m in user_msgs],
    )
    parts = [b.text for b in msg.content if hasattr(b, "text")]
    return "\n".join(parts).strip()


def detect_backend(model: str, backend: str) -> str:
    if backend != "auto":
        return backend
    if model.startswith(("gpt-", "o1", "o3", "o4")):
        return "openai"
    if model.startswith("claude"):
        return "anthropic"
    if model.startswith("deepseek"):
        return "deepseek"
    return "hf"


def generate_one(
    backend: str,
    model: str,
    item: dict,
    max_new_tokens: int,
    dtype: str,
    *,
    temperature: float = 0.0,
) -> str:
    if backend == "hf":
        return generate_hf(model, item, max_new_tokens, dtype, temperature=temperature)
    if backend == "openai":
        return generate_openai(model, item, max_new_tokens, temperature=temperature)
    if backend == "anthropic":
        return generate_anthropic(model, item, max_new_tokens, temperature=temperature)
    if backend == "deepseek":
        return generate_deepseek(model, item, max_new_tokens, temperature=temperature)
    raise ValueError(f"Unknown backend: {backend}")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    p = argparse.ArgumentParser(description="CLAIMS-Bench response generation")
    p.add_argument("--data", type=Path, default=DEFAULT_DATA)
    p.add_argument("--model", type=str, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument(
        "--backend",
        type=str,
        default="auto",
        choices=["auto", "hf", "openai", "anthropic", "deepseek"],
    )
    p.add_argument("--max-new-tokens", type=int, default=512)
    p.add_argument("--limit", type=int, default=0, help="0 = all items")
    p.add_argument("--dtype", type=str, default="auto", choices=["auto", "float16", "bfloat16"])
    p.add_argument("--resume", action="store_true", help="Skip ids already in --out")
    p.add_argument("--sleep", type=float, default=0.0, help="Seconds between API calls")
    args = p.parse_args()

    items = load_jsonl(args.data)
    if args.limit > 0:
        items = items[: args.limit]

    backend = detect_backend(args.model, args.backend)
    logger.info("Backend=%s model=%s n=%d", backend, args.model, len(items))

    done: set[str] = set()
    if args.resume and args.out.exists():
        for row in load_jsonl(args.out):
            done.add(row["id"])
        logger.info("Resuming: %d already done", len(done))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if args.resume and args.out.exists() else "w"
    written = 0
    with args.out.open(mode) as f:
        for item in tqdm(items, desc="generate"):
            if item["id"] in done:
                continue
            try:
                response = generate_one(
                    backend, args.model, item, args.max_new_tokens, args.dtype
                )
            except Exception as e:
                logger.exception("Failed on %s", item["id"])
                response = f"[GENERATION_ERROR: {e}]"
            row = {
                "id": item["id"],
                "model": args.model,
                "response": response,
                "meta": {
                    "max_new_tokens": args.max_new_tokens,
                    "backend": backend,
                    "data_version": item.get("version"),
                    "tier": item.get("tier"),
                },
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            written += 1
            if args.sleep > 0:
                time.sleep(args.sleep)

    logger.info("Wrote %d responses to %s", written, args.out)


if __name__ == "__main__":
    main()
