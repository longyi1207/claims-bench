# Source this before any run: `source scripts/env.sh`
#
# Loads repo-root .env (the canonical credential file per docs/AZURE.md) and
# derives the two vars Inspect's OpenAI-compatible provider needs so that
# `--model openai-api/azure/<deployment>` routes to Azure OpenAI on credits
# instead of api.openai.com on a personal card.
_OLD_PATH="$PATH"
set -a
. "$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)/.env"
set +a
export PATH="$_OLD_PATH"; unset _OLD_PATH

# Inspect: openai-api/<service>/<model> looks up <SERVICE>_API_KEY / <SERVICE>_BASE_URL
export AZURE_API_KEY="$AZURE_OPENAI_API_KEY"
export AZURE_BASE_URL="${AZURE_OPENAI_ENDPOINT%/}/openai/v1/"
