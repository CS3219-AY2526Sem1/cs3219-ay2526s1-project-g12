#!/bin/bash
/app/.venv/bin/aerich upgrade && /app/.venv/bin/celery --app service.feedback_ai_svc worker -c 1 --loglevel=INFO & exec /app/.venv/bin/fastapi run /app/routes.py $@
wait -n
exit $?
