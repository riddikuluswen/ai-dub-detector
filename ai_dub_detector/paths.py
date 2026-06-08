from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CACHE_DIR = PROJECT_ROOT / ".cache" / "huggingface"
DEFAULT_TMP_DIR = PROJECT_ROOT / "_work" / "tmp"
