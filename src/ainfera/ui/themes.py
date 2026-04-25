"""Ainfera Rich theme — see docs/DESIGN-SYSTEM.md."""

from rich.theme import Theme

# Brand identity (navy) for wordmark, headings, and accents.
# Status (success/warning/error/info) carries NO hue — weight and
# intensity only. See DESIGN-SYSTEM.md §6.
AINFERA_THEME = Theme(
    {
        # Brand identity — navy palette
        "ainfera.brand": "bold #2878B5",
        "ainfera.hover": "#4A9FD9",
        "ainfera.highlight": "bold #7EC4EF",
        # Status — no hue (DESIGN-SYSTEM.md §6)
        "ainfera.success": "default",
        "ainfera.warning": "dim",
        "ainfera.error": "bold",
        "ainfera.info": "italic",
        "ainfera.muted": "dim",
        # Surface / text
        "ainfera.surface": "default",
        "ainfera.text": "default",
        "ainfera.header": "bold",
        # Trust grades — no hue (DESIGN-SYSTEM.md §7)
        "trust.aaa": "bold",
        "trust.aa": "bold",
        "trust.a": "default",
        "trust.bbb": "default",
        "trust.bb": "dim",
        "trust.b": "dim",
        "trust.ccc": "bold",
    }
)


def grade_style(grade: str) -> str:
    """Return Rich style name for a trust grade."""
    return f"trust.{grade.lower()}"
