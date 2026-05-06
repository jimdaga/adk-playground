FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl && \
    rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      -o /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      > /etc/apt/sources.list.d/github-cli.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends gh && \
    rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --gecos "" agent && \
    mkdir -p /tmp/sdlc-workspace && \
    chown -R agent:agent /tmp/sdlc-workspace

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy as a proper package under /app so "coder_service" is importable
COPY . /app/coder_service/

USER agent

ENV PORT=8080
ENV PYTHONPATH=/app
CMD ["sh", "-c", "uvicorn coder_service.agent:a2a_app --host 0.0.0.0 --port $PORT"]
