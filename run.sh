#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"
exec streamlit run streamlit_app.py "$@"
