FROM python:3.15-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    AWS_LWA_READINESS_CHECK_PATH=/health

WORKDIR /srv

# Dependencies first, so this layer is cached between code changes
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app

# Lets the same image run on AWS Lambda; does nothing anywhere else
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:1.1.0 /lambda-adapter /opt/extensions/lambda-adapter

# Don't run as root
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]