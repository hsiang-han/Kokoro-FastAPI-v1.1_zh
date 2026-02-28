$env:PHONEMIZER_ESPEAK_LIBRARY="C:\Program Files\eSpeak NG\libespeak-ng.dll"
$env:PYTHONUTF8=1
$Env:PROJECT_ROOT="$pwd"
$Env:USE_GPU="false"
$Env:USE_ONNX="false"
$Env:PYTHONPATH="$Env:PROJECT_ROOT;$Env:PROJECT_ROOT/api"
$Env:MODEL_DIR="src/models"
$Env:VOICES_DIR="src/voices/v1_1_zh"
$Env:DEFAULT_VOICE="zf_094"
$Env:REPO_ID="hexgrad/Kokoro-82M-v1.1-zh"
$Env:KOKORO_V1_FILE="v1_1_zh/kokoro-v1_1-zh.pth"
$Env:WEB_PLAYER_PATH="$Env:PROJECT_ROOT/web"

uv pip install -e ".[cpu]"
uv run --no-sync python docker/scripts/download_model.py --output api/src/models/v1_1_zh --voices-output api/src/voices/v1_1_zh
uv run --no-sync uvicorn api.src.main:app --host 0.0.0.0 --port 8880