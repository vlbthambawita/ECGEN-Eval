"""MkDocs hook: show the ECGEN-Eval version in the documentation.

The version is the latest release tag (``git describe --tags``), falling back to the
installed package metadata. It is shown as a badge next to the site name, appended to
the footer, and substituted for ``{{ ecgen_version }}`` in Markdown pages
(prefix it with a backslash to show the placeholder literally).
"""

from __future__ import annotations

import html
import re
import subprocess
from importlib.metadata import PackageNotFoundError, version

_PLACEHOLDER = "{{ ecgen_version }}"
_STATE: dict = {}


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(["git", *args], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.strip() or None


def _resolve_version() -> tuple[str, str]:
    """Return (release, build) — e.g. ("0.5.0", "v0.5.0-3-gb1bbbe4")."""
    tag = _git("describe", "--tags", "--abbrev=0")
    if tag:
        return tag.lstrip("v"), _git("describe", "--tags") or tag
    try:
        pkg = version("ecgen-eval")
    except PackageNotFoundError:
        return "unknown", "unknown"
    return pkg.split("+")[0], pkg


def on_config(config, **kwargs):
    release, build = _resolve_version()
    _STATE.update(release=release, build=build)
    config.extra["ecgen_version"] = release
    suffix = f"ECGEN-Eval v{release}"
    config.copyright = f"{config.copyright} · {suffix}" if config.copyright else suffix
    return config


def on_page_markdown(markdown, **kwargs):
    escaped = "\\" + _PLACEHOLDER
    parts = markdown.split(escaped)
    parts = [p.replace(_PLACEHOLDER, _STATE.get("release", "unknown")) for p in parts]
    return _PLACEHOLDER.join(parts)


def on_post_page(output, config, **kwargs):
    release, build = _STATE.get("release"), _STATE.get("build")
    if not release or release == "unknown":
        return output
    badge = (
        f'<span class="ecgen-version" title="Documentation built from {html.escape(build)}">'
        f"v{html.escape(release)}</span>"
    )
    # First occurrence of the site name in the header title.
    pattern = re.compile(
        r'(<div class="md-header__topic">\s*<span class="md-ellipsis">\s*'
        + re.escape(config.site_name)
        + r")(\s*</span>)"
    )
    return pattern.sub(lambda m: m.group(1) + " " + badge + m.group(2), output, count=1)
