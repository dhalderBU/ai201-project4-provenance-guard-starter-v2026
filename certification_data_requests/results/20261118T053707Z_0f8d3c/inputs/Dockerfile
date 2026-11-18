FROM python:3.12-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HOST=0.0.0.0 \
    PORT=5000 \
    AI201_DEBUG=0 \
    HF_HOME=/models

WORKDIR /app

COPY requirements-docker.lock ./
RUN python -m pip install --no-cache-dir --require-hashes -r requirements-docker.lock

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --create-home app \
    && mkdir -p /app/logs /app/results /models \
    && chown -R app:app /app/logs /app/results /models

# .dockerignore limits this to source, documentation, dependency definitions,
# and small input fixtures. Existing logs/results and downloaded data stay out.
COPY . ./

USER app
EXPOSE 5000

# Liveness only: /health's inference_ready field separately reports readiness.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=4)"

# One HTTP worker shares rate-limit and circuit-breaker state. Threads allow
# health/metrics and fast overload responses while the isolated model job runs.
CMD ["gunicorn", "--config", "gunicorn_conf.py", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "300", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
