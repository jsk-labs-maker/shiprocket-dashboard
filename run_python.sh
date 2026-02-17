#!/bin/bash
# Helper script to run python with venv
cd "$(dirname "$0")"
.venv/bin/python "$@"
