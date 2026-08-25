"""OpenAI client routing: Azure OpenAI by default, direct OpenAI as fallback.

Repo policy (`../../docs/AZURE.md`): prefer Azure OpenAI — LY has Azure credits;
direct `OPENAI_API_KEY` bills a personal card. Every OpenAI call in this project
(generation *and* judges) goes through `openai_client()`.

Routing, in order:
  1. `OPENAI_PREFER_AZURE` truthy AND `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_ENDPOINT`
     set -> Azure OpenAI via its OpenAI-compatible v1 endpoint.
  2. else `OPENAI_API_KEY` -> api.openai.com.
  3. else raise.

On Azure the `model` argument must be a **deployment name**, not a base model id.
The deployments in this project's Azure resource are named after their models
(`gpt-4o` -> gpt-4o 2024-11-20, `gpt-4o-mini` -> gpt-4o-mini 2024-07-18), so the
mapping is the identity by default; override per-model with
`AZURE_DEPLOYMENT_MAP="gpt-4o=my-4o-deploy,gpt-4o-mini=my-mini"`.

Note for anyone reading the results: Azure applies content filtering that
api.openai.com does not. Several L3 items are historically sensitive (1943
Netherlands harboring, colonial rebellion, refusing a kill order). A filtered
refusal is an artifact of the *deployment*, not a value commitment of the model —
`scripts/provider_parity_check.py` exists to detect exactly that.
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_TRUTHY = {"1", "true", "yes", "on"}


def prefer_azure() -> bool:
    return os.environ.get("OPENAI_PREFER_AZURE", "true").strip().lower() in _TRUTHY


def azure_configured() -> bool:
    return bool(os.environ.get("AZURE_OPENAI_API_KEY") and os.environ.get("AZURE_OPENAI_ENDPOINT"))


def azure_base_url() -> str:
    """Azure's OpenAI-compatible v1 base URL (works with the stock `OpenAI` client)."""
    endpoint = (os.environ.get("AZURE_OPENAI_ENDPOINT") or "").rstrip("/")
    if not endpoint:
        raise RuntimeError("AZURE_OPENAI_ENDPOINT is not set")
    return f"{endpoint}/openai/v1/"


def _deployment_map() -> dict[str, str]:
    raw = os.environ.get("AZURE_DEPLOYMENT_MAP", "")
    out: dict[str, str] = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if "=" in pair:
            model, deployment = pair.split("=", 1)
            out[model.strip()] = deployment.strip()
    return out


def resolve_model(model: str) -> str:
    """Model id -> Azure deployment name (identity unless overridden)."""
    if not using_azure():
        return model
    return _deployment_map().get(model, model)


def using_azure() -> bool:
    return prefer_azure() and azure_configured()


# The legacy scorer has no retry of its own: a 429 becomes a silently dropped
# sample. Azure per-deployment TPM is easy to exceed with concurrent judge
# workers, so give the SDK a real retry budget rather than its default of 2.
DEFAULT_MAX_RETRIES = int(os.environ.get("OPENAI_MAX_RETRIES", "8"))


def openai_client(**kwargs: Any):
    """An `openai.OpenAI` client pointed at Azure or api.openai.com."""
    from openai import OpenAI

    kwargs.setdefault("max_retries", DEFAULT_MAX_RETRIES)
    if using_azure():
        return OpenAI(
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            base_url=azure_base_url(),
            **kwargs,
        )
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "No OpenAI credentials: set AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT "
            "(preferred, see docs/AZURE.md) or OPENAI_API_KEY."
        )
    logger.warning(
        "Falling back to direct OpenAI (api.openai.com) — this bills a personal card, "
        "not Azure credits. Set AZURE_OPENAI_* to use credits."
    )
    return OpenAI(**kwargs)


def provider_label() -> str:
    """Short string for logging / spend rows."""
    return "azure-openai" if using_azure() else "openai"


# --------------------------------------------------------------------------- #
# Azure content filtering
# --------------------------------------------------------------------------- #
#
# Measured 2026-08-24 over all 80 L3 items (`outputs/azure_content_filter_scan.json`,
# `outputs/azure_judge_filter_scan.json`):
#   generation blocked 1/80 — revelation_064 (My Lai, 1968): jailbreak + violence/medium
#   judge      blocked 1/80 — revelation_066 (1933 "Aryan business" pledge): hate/medium
#
# A custom RAI policy (`research-permissive`: all four categories at severity
# "High", jailbreak/indirect-attack disabled) was created and attached to both
# deployments; ARM accepts it but the data plane still blocks these two. Relaxing
# Azure filters below the default needs Microsoft's modified-content-filter
# approval, which is an application, not a setting.
#
# The point of this benchmark is measuring what a model reveals under moral
# conflict. A deployment-level refusal is NOT that, so it must never be scored as
# if it were the model's answer — hence a distinct marker and parse status.

PROVIDER_FILTERED_PREFIX = "[PROVIDER_FILTERED:"


def is_content_filter_error(exc: BaseException) -> bool:
    """True if an OpenAI/Azure exception is a content-filter rejection."""
    body = getattr(exc, "body", None) or {}
    if isinstance(body, dict):
        if body.get("code") == "content_filter":
            return True
        inner = body.get("innererror") or {}
        if inner.get("code") == "ResponsibleAIPolicyViolation":
            return True
    return "content_filter" in str(exc) or "content management policy" in str(exc)


def content_filter_categories(exc: BaseException) -> dict:
    body = getattr(exc, "body", None) or {}
    inner = (body.get("innererror") or {}) if isinstance(body, dict) else {}
    cfr = inner.get("content_filter_result") or {}
    return {k: v for k, v in cfr.items() if v.get("filtered") or v.get("detected")}


def allow_openai_filter_fallback() -> bool:
    """Opt-in: retry a content-filtered call on api.openai.com.

    Default OFF — repo policy is Azure credits, not a personal card. Affects one
    call per model per run (~$0.001), so flipping it on is about data
    completeness, not cost. Set `ALLOW_OPENAI_FILTER_FALLBACK=1` to enable.
    """
    return os.environ.get("ALLOW_OPENAI_FILTER_FALLBACK", "").strip().lower() in _TRUTHY


def direct_openai_client(**kwargs: Any):
    """api.openai.com regardless of Azure preference (fallback path only)."""
    from openai import OpenAI

    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not set — cannot use the filter fallback")
    kwargs.setdefault("max_retries", DEFAULT_MAX_RETRIES)
    return OpenAI(**kwargs)


# Azure does not always signal filtering with a 400. For some deployments it
# returns HTTP 200 whose *completion text* is the filter notice — measured
# 2026-08-25: `gpt-4o-mini` returned it as content for all 10 replicates of
# revelation_064, while `gpt-4o` returned it for 3 of 10 (the filter is not
# deterministic, so it also skews replicate distributions). Detecting only the
# 400 path lets those rows enter the dataset as if the model had answered.
FILTERED_RESPONSE_MARKERS = (
    "filtered due to the prompt triggering azure openai's content management policy",
    "the response was filtered due to the prompt triggering",
    "filtered due to the response triggering azure openai's content management policy",
)


def looks_like_filter_response(text: str) -> bool:
    """True if a *successful* completion is really a content-filter notice."""
    low = (text or "").strip().lower()
    if not low:
        return False
    # The notice is the whole body, not a passing mention inside a long answer.
    return len(low) < 800 and any(m in low for m in FILTERED_RESPONSE_MARKERS)
