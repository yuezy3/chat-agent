#!/bin/bash
app_root=$(dirname $(readlink -f $0))
cd "$app_root"
source venv/bin/activate # active venv
uvicorn main:app --host 0.0.0.0 --port 3000
