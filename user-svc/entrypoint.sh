#!/bin/bash
/app/.venv/bin/alembic upgrade head && exec /app/.venv/bin/fastapi run /app/main.py $@
