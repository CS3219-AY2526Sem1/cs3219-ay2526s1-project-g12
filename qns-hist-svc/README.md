# Question History Backend

### Usage

This service includes the usage of Celery Task Queue.

Please run the worker with:
```
uv run celery --app service.feedback_ai_svc worker -c 1 --loglevel=INFO
```
