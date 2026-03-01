FROM rocm/dev-ubuntu-24.04:6.4.4-complete
ENV DEBIAN_FRONTEND=noninteractive \
    PHONEMIZER_ESPEAK_PATH=/usr/bin \
    PHONEMIZER_ESPEAK_DATA=/usr/share/espeak-ng-data \
    ESPEAK_DATA_PATH=/usr/share/espeak-ng-data

# Install Python and other dependencies
RUN apt-get update && apt upgrade -y && apt-get install -y --no-install-recommends \
    espeak-ng \
    espeak-ng-data \
    rocrand \
    git \
    libsndfile1 \
    curl \
    ffmpeg \
    wget \
    nano \
    g++ \
    zstd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /usr/share/espeak-ng-data \
    && ln -s /usr/lib/*/espeak-ng-data/* /usr/share/espeak-ng-data/ \

    # Install UV using the installer script
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/ \
    && mv /root/.local/bin/uvx /usr/local/bin/ \

    # Create non-root user and set up directories and permissions
        && if getent passwd 1000 >/dev/null; then \
                 EXISTING_USER="$(getent passwd 1000 | cut -d: -f1)"; \
                 if [ "$EXISTING_USER" != "appuser" ]; then usermod -l appuser "$EXISTING_USER"; fi; \
                 usermod -d /home/appuser -m appuser || true; \
             else \
                 useradd -m -u 1000 appuser; \
             fi \
        && APP_GID="$(id -g appuser)" \
        && getent group appuser >/dev/null || groupadd -g "$APP_GID" -o appuser \
        && usermod -g appuser appuser \
    && mkdir -p /app/api/src/models/v1_1_zh /app/api/src/voices/v1_1_zh \
    && chown -R appuser:appuser /app \
    # Models folder
    && mkdir -p /app/api/src/models/v1_1_zh

USER appuser
WORKDIR /app

# Copy dependency files
COPY --chown=appuser:appuser pyproject.toml ./pyproject.toml

ENV PHONEMIZER_ESPEAK_PATH=/usr/bin \
    PHONEMIZER_ESPEAK_DATA=/usr/share/espeak-ng-data \
    ESPEAK_DATA_PATH=/usr/share/espeak-ng-data

# Install dependencies with GPU extras (using cache mounts)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv --python 3.12 && \
    uv sync --extra rocm

# Run kdb files (shape files for MIOpen)
ENV ROCM_VERSION=6.4.4
COPY --chown=appuser:appuser docker/rocm/kdb_install.sh /tmp/
RUN /tmp/kdb_install.sh

# Support older GFX Arch
ENV ROCBLAS_VERSION=6.4.4-1
RUN cd /tmp && wget https://archive.archlinux.org/packages/r/rocblas/rocblas-${ROCBLAS_VERSION}-x86_64.pkg.tar.zst -O rocblas.tar.zst \
    && pwd && ls -lah ./ \
    && tar --zstd -xvf rocblas.tar.zst && rm rocblas.tar.zst \
    && rm -rf /app/.venv/lib/python3.12/site-packages/torch/lib/rocblas/library/ \
    && mv ./opt/rocm/lib/rocblas/library/ /app/.venv/lib/python3.12/site-packages/torch/lib/rocblas/

# Copy project files including models
COPY --chown=appuser:appuser api ./api
COPY --chown=appuser:appuser web ./web
COPY --chown=appuser:appuser docker/scripts/ ./

RUN chmod +x ./entrypoint.sh

# Set all environment variables in one go
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/api \
    PATH="/app/.venv/bin:$PATH" \
    UV_LINK_MODE=copy \
    USE_GPU=true \
    REPO_ID=hexgrad/Kokoro-82M-v1.1-zh \
    DEFAULT_VOICE=zf_094 \
    KOKORO_V1_FILE=v1_1_zh/kokoro-v1_1-zh.pth \
    VOICES_DIR=/app/api/src/voices/v1_1_zh \
    DOWNLOAD_MODEL=true \
    DEVICE="gpu"

# Run FastAPI server through entrypoint.sh
CMD ["./entrypoint.sh"]
