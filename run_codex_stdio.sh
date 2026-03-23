#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON_BIN="$ROOT/.venv/bin/python"

if [ ! -x "$PYTHON_BIN" ]; then
  echo "Missing $PYTHON_BIN. Create .venv and install requirements first." >&2
  exit 1
fi

if [ -f "$ROOT/.env" ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      ''|\#*)
        continue
        ;;
      *=*)
        key=${line%%=*}
        value=${line#*=}
        eval "is_set=\${$key+x}"
        if [ -z "${is_set:-}" ]; then
          export "$key=$value"
        fi
        ;;
    esac
  done < "$ROOT/.env"
fi

export MCP_TRANSPORT=stdio
exec "$PYTHON_BIN" "$ROOT/server.py" --transport stdio
