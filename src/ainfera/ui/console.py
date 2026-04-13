"""Rich console singleton with Ainfera branding."""

from rich.console import Console

from .themes import AINFERA_THEME

console = Console(theme=AINFERA_THEME)
err_console = Console(theme=AINFERA_THEME, stderr=True)


def print_header():
    """Print Ainfera CLI header banner."""
    console.print()
    console.print("  [ainfera.brand]\u25c6 AINFERA[/ainfera.brand]", highlight=False)
    console.print(
        "  [ainfera.muted]The unified infrastructure for AI agents[/ainfera.muted]"
    )
    console.print()


def print_error(message: str, hint: str = ""):
    """Print formatted error with optional hint."""
    err_console.print(f"  [ainfera.error]\u2717 Error:[/ainfera.error] {message}")
    if hint:
        err_console.print(f"  [ainfera.muted]\u2192 {hint}[/ainfera.muted]")


def print_success(message: str):
    """Print formatted success message."""
    console.print(f"  [ainfera.success]\u2713[/ainfera.success] {message}")


def print_warning(message: str):
    """Print formatted warning message."""
    console.print(f"  [ainfera.warning]\u26a0[/ainfera.warning] {message}")


def print_info(message: str):
    """Print formatted info message."""
    console.print(f"  [ainfera.info]\u25b8[/ainfera.info] {message}")


def print_step(label: str, detail: str = "", done: bool = False):
    """Print a deploy-style step line."""
    mark = "[ainfera.success]\u2713[/ainfera.success]" if done else "[ainfera.info]\u25b8[/ainfera.info]"
    suffix = f"  {detail}" if detail else ""
    console.print(f"  {mark} {label}{suffix}")
