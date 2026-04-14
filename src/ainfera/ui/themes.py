"""Ainfera Rich theme and color constants."""

from rich.theme import Theme

# Ainfera DS v2 — navy brand palette
AINFERA_THEME = Theme(
    {
        "ainfera.brand": "bold #2878B5",
        "ainfera.hover": "#4A9FD9",
        "ainfera.highlight": "bold #7EC4EF",
        "ainfera.success": "bold #5B8C6A",
        "ainfera.warning": "#D4A43A",
        "ainfera.error": "bold #C4453A",
        "ainfera.info": "#4A9FD9",
        "ainfera.muted": "#64748B",
        "ainfera.surface": "#001E41",
        "ainfera.text": "#F7F5F0",
        "ainfera.header": "bold #F7F5F0 on #001E41",
        # Trust grade colors
        "trust.aaa": "bold #5B8C6A",
        "trust.aa": "#5B8C6A",
        "trust.a": "#6B9C5A",
        "trust.bbb": "#2878B5",
        "trust.bb": "#D4A43A",
        "trust.b": "#E07A3A",
        "trust.ccc": "bold #C4453A",
    }
)


def grade_style(grade: str) -> str:
    """Return Rich style name for a trust grade."""
    return f"trust.{grade.lower()}"
