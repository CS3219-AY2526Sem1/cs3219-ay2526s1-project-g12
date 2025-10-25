#!/bin/bash
/app/.venv/bin/aerich upgrade && exec /app/.venv/bin/fastapi run /app/routes.py $@
