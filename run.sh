#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
venv_python="${project_root}/.venv/bin/python"

if [[ ! -x "${venv_python}" ]]; then
  echo "No se encontro .venv/bin/python. Crea la venv con: /usr/bin/python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt" >&2
  exit 1
fi

exec "${venv_python}" "${project_root}/main.py" "$@"
