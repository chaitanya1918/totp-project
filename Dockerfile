############################
# Stage 1: Builder
############################
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt


############################
# Stage 2: Runtime
############################
FROM python:3.11-slim AS runtime

ENV TZ=UTC

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends cron tzdata && \
    rm -rf /var/lib/apt/lists/*

RUN ln -snf /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "UTC" > /etc/timezone

COPY --from=builder /install /usr/local

COPY . /app

# 👇 NEW: install cron job from /app/cron/2fa-cron
RUN chmod 0644 /app/cron/2fa-cron && crontab /app/cron/2fa-cron

RUN mkdir -p /data /cron && chmod 755 /data /cron

EXPOSE 8080

CMD ["sh", "-c", "cron && uvicorn main:app --host 0.0.0.0 --port 8080"]
