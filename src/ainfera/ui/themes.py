"""Ainfera Rich theme and color constants."""

from rich.theme import Theme

# Ainfera brand colors mapped to Rich styles
AINFERA_THEME = Theme(
    {
        "ainfera.brand": "bold #C4922A",  # Aureate
        "ainfera.success": "bold #5B8C6A",  # Sage
        "ainfera.error": "bold #C4453A",  # Vermillion
        "ainfera.warning": "#D4A43A",  # Saffron
        "ainfera.info": "#4A7FB5",  # Dusk Blue
        "ainfera.muted": "#64748B",  # Steel
        "ainfera.highlight": "bold #E07A3A",  # Ember
        "ainfera.header": "bold #F7F5F0 on #0F1419",  # Ivory on Obsidian
        # Trust grade colors
        "trust.aaa": "bold #5B8C6A",
        "trust.aa": "#5B8C6A",
        "trust.a": "#6B9C5A",
        "trust.bbb": "#C4922A",
        "trust.bb": "#D4A43A",
        "trust.b": "#E07A3A",
        "trust.ccc": "bold #C4453A",
    }
)


def grade_style(grade: str) -> str:
    """Return Rich style name for a trust grade."""
    return f"trust.{grade.lower()}"
