#!/usr/bin/env python3
"""Download and prepare Kokoro v1.1-zh model + voices from HuggingFace."""

import json
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from loguru import logger

REPO_ID = "hexgrad/Kokoro-82M-v1.1-zh"
MODEL_FILE = "kokoro-v1_1-zh.pth"
CONFIG_FILE = "config.json"


def verify_model_files(model_dir: str) -> bool:
    """Verify required model files are present and valid."""
    model_path = os.path.join(model_dir, MODEL_FILE)
    config_path = os.path.join(model_dir, CONFIG_FILE)

    try:
        if not os.path.exists(model_path) or not os.path.exists(config_path):
            return False
        if os.path.getsize(model_path) == 0:
            return False
        with open(config_path, encoding="utf-8") as file_handle:
            json.load(file_handle)
        return True
    except Exception:
        return False


def verify_voice_files(voices_dir: str) -> bool:
    """Verify at least one voice file exists."""
    voice_dir_path = Path(voices_dir)
    return voice_dir_path.exists() and any(voice_dir_path.glob("*.pt"))


def _copy_if_missing(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(src, dst)


def download_model(output_dir: str, voices_output_dir: str) -> None:
    """Download model files and voices from HuggingFace.

    Args:
        output_dir: Directory for model files (`kokoro-v1_1-zh.pth`, `config.json`)
        voices_output_dir: Directory for voice `.pt` files
    """
    try:
        from huggingface_hub import snapshot_download
    except ImportError as error:
        logger.error(
            "huggingface_hub is required to download model files. Install via: uv pip install huggingface_hub"
        )
        raise RuntimeError("huggingface_hub not available") from error

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(voices_output_dir, exist_ok=True)

    has_model = verify_model_files(output_dir)
    has_voices = verify_voice_files(voices_output_dir)
    if has_model and has_voices:
        logger.info("Model and voice files already exist and are valid")
        return

    logger.info(f"Downloading {REPO_ID} resources from HuggingFace")

    try:
        with TemporaryDirectory() as tmp_dir:
            snapshot_path = snapshot_download(
                repo_id=REPO_ID,
                local_dir=tmp_dir,
                allow_patterns=[MODEL_FILE, CONFIG_FILE, "voices/*.pt"],
            )

            snapshot_root = Path(snapshot_path)
            _copy_if_missing(
                snapshot_root / MODEL_FILE,
                Path(output_dir) / MODEL_FILE,
            )
            _copy_if_missing(
                snapshot_root / CONFIG_FILE,
                Path(output_dir) / CONFIG_FILE,
            )

            for voice_file in (snapshot_root / "voices").glob("*.pt"):
                _copy_if_missing(voice_file, Path(voices_output_dir) / voice_file.name)

    except Exception as error:
        logger.error(f"Failed to download model from HuggingFace: {error}")
        logger.error(
            "Manual fallback: git clone https://huggingface.co/hexgrad/Kokoro-82M-v1.1-zh and copy model + voices into your mounted directories."
        )
        raise

    if not verify_model_files(output_dir):
        raise RuntimeError("Downloaded model files failed verification")
    if not verify_voice_files(voices_output_dir):
        raise RuntimeError("Downloaded voice files failed verification")

    logger.info(f"✓ Model files prepared in {output_dir}")
    logger.info(f"✓ Voice files prepared in {voices_output_dir}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Download Kokoro v1.1-zh model")
    parser.add_argument(
        "--output", required=True, help="Output directory for model files"
    )
    parser.add_argument(
        "--voices-output",
        required=False,
        help="Output directory for voice files (defaults to sibling voices/v1_1_zh)",
    )

    args = parser.parse_args()
    voices_output = args.voices_output
    if not voices_output:
        output_path = Path(args.output)
        voices_output = str(
            output_path.parent.parent / "voices" / output_path.name
        )

    download_model(args.output, voices_output)


if __name__ == "__main__":
    main()
