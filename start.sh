#!/usr/bin/env bash
set -e
export $(grep -v '^#' .env | xargs)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
