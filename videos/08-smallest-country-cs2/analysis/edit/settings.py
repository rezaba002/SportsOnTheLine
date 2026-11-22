import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
EDITION = HERE.parent
ROOT = EDITION.parents[1]
V1 = ROOT / "video08/codex"
PUBLIC = ROOT / "sotl-graphics/public/video08-codex-v2"
SOURCE = ROOT / "sotl-graphics/src/video08-codex-v2"
BIN = ROOT / "sotl-graphics/node_modules/@remotion/compositor-win32-x64-msvc"
FFPROBE = BIN / "ffprobe.exe"
# EDIT ME: path to ffmpeg. "ffmpeg" uses the one on your PATH.
FFMPEG = Path(shutil.which("ffmpeg") or "ffmpeg")
PYTHON = Path(r"C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1112-737-0_26.1112.737.0_x64__3k8sg7r9htsxt\dependencies\python\python.exe")


def prepare():
    for p in [PUBLIC, SOURCE, HERE / "qa", HERE / "renders", HERE / "voice", EDITION / "final"]:
        p.mkdir(parents=True, exist_ok=True)
