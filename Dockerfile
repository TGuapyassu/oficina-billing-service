FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 git && rm -rf /var/lib/apt/lists/*
ARG CONTRACTS_GIT_URL=https://github.com/TGuapyassu/oficina-contracts.git@v0.1.0
RUN pip install --no-cache-dir "oficina-contracts @ git+${CONTRACTS_GIT_URL}"
COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir -e .
EXPOSE 8003
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
