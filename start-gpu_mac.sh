#!/bin/bash

# Get project root directory
PROJECT_ROOT=$(pwd)

# Set other environment variables
export USE_GPU=true
export USE_ONNX=false
export PYTHONPATH=$PROJECT_ROOT:$PROJECT_ROOT/api
export MODEL_DIR=src/models
export VOICES_DIR=src/voices/v1_1_zh
export DEFAULT_VOICE=zf_094
export REPO_ID=hexgrad/Kokoro-82M-v1.1-zh
export KOKORO_V1_FILE=v1_1_zh/kokoro-v1_1-zh.pth
export WEB_PLAYER_PATH=$PROJECT_ROOT/web

export DEVICE_TYPE=mps
# Enable MPS fallback for unsupported operations
export PYTORCH_ENABLE_MPS_FALLBACK=1

# Run FastAPI with GPU extras using uv run
uv pip install -e .
uv run --no-sync python docker/scripts/download_model.py --output api/src/models/v1_1_zh --voices-output api/src/voices/v1_1_zh
uv run --no-sync uvicorn api.src.main:app --host 0.0.0.0 --port 8880
