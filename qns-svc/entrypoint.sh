#!/bin/bash
/app/.venv/bin/aerich upgrade && /app/.venv/bin/fastapi run /app/routes.py
