"""Framework auto-detection for AI agent projects."""

from __future__ import annotations

import json
import re
from pathlib import Path

# Framework markers: (package_name, framework_id)
_PYTHON_FRAMEWORKS = [
    ("langgraph", "langchain"),
    ("langchain", "langchain"),
    ("crewai", "crewai"),
    ("openclaw", "openclaw"),
    ("openai", "openai_sdk"),
    # Q4 2026: ("pyautogen", "autogen"), ("google-adk", "adk"),
    # ("llamaindex", "llamaindex"), ("semantic-kernel", "semantic-kernel"),
]

_JS_FRAMEWORKS = [
    ("langchain", "langchain"),
    ("openai", "openai_sdk"),
    # Q4 2026: ("@google/genai", "adk"),
]


def _search_file_for_packages(
    filepath: Path, packages: list[tuple[str, str]]
) -> tuple[str, str, str | None] | None:
    """Search a file for package references. Returns (framework, source, version)."""
    try:
        content = filepath.read_text()
    except (OSError, UnicodeDecodeError):
        return None

    for pkg, framework in packages:
        # Match patterns like: package==1.2.3, package>=1.0, "package": "^1.0"
        pattern = re.compile(
            rf'(?:^|\s|"|\'|,){re.escape(pkg)}(?:[=><!~\s"\',\]]|$)', re.IGNORECASE
        )
        if pattern.search(content):
            # Try to extract version
            ver_match = re.search(
                rf'{re.escape(pkg)}[=><!~]+\s*([\d.]+)', content
            )
            version = ver_match.group(1) if ver_match else None
            return framework, filepath.name, version

    return None


def detect_framework(path: str = ".") -> tuple[str, dict]:
    """Detect AI agent framework from project files.

    Returns: (framework_name, detection_details)
    """
    root = Path(path)

    # Check Python dependency files
    for fname in ("requirements.txt", "pyproject.toml", "setup.py", "setup.cfg"):
        fpath = root / fname
        if fpath.exists():
            result = _search_file_for_packages(fpath, _PYTHON_FRAMEWORKS)
            if result:
                fw, source, version = result
                return fw, {
                    "framework": fw,
                    "source_file": source,
                    "version": version,
                    "confidence": "high" if version else "medium",
                }

    # Check Node.js
    pkg_json = root / "package.json"
    if pkg_json.exists():
        try:
            data = json.loads(pkg_json.read_text())
            all_deps = {
                **data.get("dependencies", {}),
                **data.get("devDependencies", {}),
            }
            for pkg, framework in _JS_FRAMEWORKS:
                if pkg in all_deps:
                    version = all_deps[pkg].lstrip("^~>=<")
                    return framework, {
                        "framework": framework,
                        "source_file": "package.json",
                        "version": version if version else None,
                        "confidence": "high",
                    }
        except (json.JSONDecodeError, OSError):
            pass

    return "custom", {
        "framework": "custom",
        "source_file": None,
        "version": None,
        "confidence": "low",
    }


def detect_entrypoint(path: str = ".") -> str | None:
    """Detect the main entry point file."""
    root = Path(path)
    candidates = [
        ("main.py", "main"),
        ("agent/main.py", "agent.main"),
        ("app.py", "app"),
        ("src/main.py", "src.main"),
        ("agent.py", "agent"),
        ("run.py", "run"),
    ]
    for filepath, module in candidates:
        if (root / filepath).exists():
            return module
    return None


def detect_python_version(path: str = ".") -> str:
    """Detect Python version from project files."""
    root = Path(path)

    # .python-version file
    pv_file = root / ".python-version"
    if pv_file.exists():
        try:
            version = pv_file.read_text().strip()
            if version:
                return version
        except OSError:
            pass

    # pyproject.toml requires-python
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            match = re.search(r'requires-python\s*=\s*"[>=<]*(\d+\.\d+)"', content)
            if match:
                return match.group(1)
        except OSError:
            pass

    return "3.12"
