# syntax=docker/dockerfile:1
FROM python:3.11-slim
COPY experiments/aasx/requirements.txt /tools/requirements.txt
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; \
    python -m pip install --no-cache-dir pip==24.0 && \
    python -m pip install --no-cache-dir -r /tools/requirements.txt
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /tmp
ENTRYPOINT ["python", "/repo/experiments/run_aasx_exp06.py"]
