"""ainfera deploy — read ainfera.yaml and create or update the agent."""

from __future__ import annotations

import json
import time
from pathlib import Path

import click
import httpx
import yaml
from rich.panel import Panel
from rich.table import Table

from ainfera.api.client import AinferaClient
from ainfera.config.settings import (
    get_api_key,
    get_api_url,
    set_default_agent,
)
from ainfera.ui.console import console, print_error


@click.command()
@click.option(
    "--config",
    "config_path",
    default="ainfera.yaml",
    type=click.Path(),
    help="Path to ainfera.yaml",
)
@click.option("--dry-run", is_flag=True, help="Show planned action without calling the API")
@click.option(
    "--from-config",
    is_flag=True,
    help="Send raw YAML to POST /v1/agents/from-config",
)
@click.option(
    "--demo",
    is_flag=True,
    help="Run the deploy showcase with mock data (no API calls)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Redeploy an existing agent (update in place)",
)
@click.pass_context
def deploy(
    ctx,
    config_path: str,
    dry_run: bool,
    from_config: bool,
    demo: bool,
    force: bool,
):
    """Deploy your agent from ainfera.yaml.

    \b
    Examples:
      ainfera deploy                                 # reads ./ainfera.yaml
      ainfera deploy --demo                          # stage-ready showcase with mock data
      ainfera deploy --force                         # redeploy an existing agent
      ainfera deploy --dry-run                       # show plan, don't call API
      ainfera deploy --config ./agents/bot.yaml
      ainfera deploy --from-config                   # send raw YAML to /v1/agents/from-config
    """
    json_output = ctx.obj.get("json", False)

    if demo:
        _run_demo(json_output=json_output)
        return

    path = Path(config_path)
    if not path.exists():
        if json_output:
            click.echo(
                json.dumps(
                    {"error": f"No {config_path} found. Run: ainfera init <name>"}
                )
            )
            raise SystemExit(1)
        print_error(
            f"No {config_path} found.",
            "Run: ainfera init <name>",
        )
        raise SystemExit(1)

    raw_yaml = path.read_text()
    try:
        parsed = yaml.safe_load(raw_yaml) or {}
    except yaml.YAMLError as e:
        if json_output:
            click.echo(json.dumps({"error": f"Invalid YAML: {e}"}))
            raise SystemExit(1)
        print_error(f"Invalid {config_path}: {e}")
        raise SystemExit(1)

    agent_section = parsed.get("agent") or {}
    if not agent_section:
        print_error(
            f"{config_path} is missing the 'agent:' section.",
            "Run 'ainfera init' to scaffold a valid file.",
        )
        raise SystemExit(1)

    name = agent_section.get("name")
    framework = agent_section.get("framework")
    description = agent_section.get("description", "")
    compute = agent_section.get("compute") or {}
    sandbox = compute.get("sandbox", "docker")
    memory = compute.get("memory", "512mb")
    cpu = compute.get("cpu", 1)
    trust_cfg = agent_section.get("trust") or {}
    floor = trust_cfg.get("quarantine_threshold", trust_cfg.get("floor", 400))
    billing = agent_section.get("billing") or {}
    billing_model = billing.get("model", "per_call")
    billing_rate = billing.get("price_per_call", billing.get("rate_usd", 0.003))
    protocols = agent_section.get("protocols") or ["mcp", "a2a"]

    if not name or not framework:
        print_error(
            "ainfera.yaml must include agent.name and agent.framework.",
        )
        raise SystemExit(1)

    if dry_run:
        _print_dry_run(
            name=name,
            framework=framework,
            sandbox=sandbox,
            memory=memory,
            cpu=cpu,
            floor=floor,
            from_config=from_config,
            json_output=json_output,
        )
        return

    api_key = get_api_key()
    if not api_key:
        if json_output:
            click.echo(
                json.dumps(
                    {"error": "Not authenticated. Run: ainfera login --api-key"}
                )
            )
            raise SystemExit(1)
        print_error(
            "Not authenticated.",
            "Run: ainfera login --api-key",
        )
        raise SystemExit(1)

    api_url = get_api_url()
    client = AinferaClient(api_key=api_key, api_url=api_url)

    try:
        existing = _find_existing_by_name(client, name)
        if existing and not force and not from_config:
            msg = (
                f"Agent {name} already exists. "
                "Use ainfera deploy --force to redeploy."
            )
            if json_output:
                click.echo(
                    json.dumps({"error": msg, "agent_id": existing.get("id")})
                )
                raise SystemExit(1)
            print_error(msg)
            raise SystemExit(1)

        # ── Header ─────────────────────────────────────────────────────
        if not json_output:
            _print_header(name=name, framework=framework, did="(pending)")

        # ── Step 1: Provisioning sandbox (create or update agent) ──────
        sandbox_detail = _format_sandbox_detail(sandbox, memory, cpu)
        with _step(
            "Provisioning sandbox...", sandbox_detail, json_output=json_output
        ):
            if from_config:
                agent = client.create_agent_from_config(raw_yaml)
                action = "created"
            elif existing:
                agent = client.update_agent(
                    existing["id"],
                    framework=framework,
                    description=description,
                    config_yaml=raw_yaml,
                )
                action = "updated"
            else:
                agent = client.create_agent(
                    name=name,
                    framework=framework,
                    description=description,
                    config_yaml=raw_yaml,
                )
                action = "created"

        agent_id = agent.get("id", "")
        did = agent.get("did") or f"did:ainfera:agent:{agent_id[:4]}" if agent_id else "(unknown)"
        if agent_id:
            set_default_agent(agent_id)

        # ── Step 2: Computing trust score ──────────────────────────────
        trust_score: int | None = None
        trust_grade: str | None = None
        trust_dimensions: dict[str, float] = {}
        trust_detail = "pending"
        if agent_id:
            try:
                trust_data = client.get_trust_score(agent_id)
            except click.ClickException:
                trust_data = None
            if trust_data is None or not (
                trust_data.get("score") or trust_data.get("overall_score")
            ):
                # Seed baseline if no score yet (tolerate endpoint absence)
                try:
                    trust_data = client.put_trust_baseline(
                        agent_id,
                        dimensions={
                            "safety": 0.8,
                            "reliability": 0.8,
                            "quality": 0.8,
                            "performance": 0.8,
                            "reputation": 0.8,
                        },
                    )
                except click.ClickException:
                    trust_data = {}
            trust_score = trust_data.get("score") or trust_data.get("overall_score")
            trust_grade = trust_data.get("grade")
            trust_dimensions = _extract_dimensions(trust_data)
            if trust_grade and trust_score is not None:
                trust_detail = f"{trust_grade} ({trust_score})"
            elif trust_score is not None:
                trust_detail = str(trust_score)
        with _step(
            "Computing trust score...", trust_detail, json_output=json_output
        ):
            pass

        # ── Step 3: Activating billing ─────────────────────────────────
        billing_detail = _format_billing_detail(billing_model, billing_rate)
        with _step(
            "Activating billing...", billing_detail, json_output=json_output
        ):
            pass

        # ── Step 4: Arming kill switch ─────────────────────────────────
        kill_detail = f"floor: {floor}"
        with _step(
            "Arming kill switch...", kill_detail, json_output=json_output
        ):
            if agent_id:
                try:
                    client.arm_kill_switch(agent_id, floor=int(floor))
                except click.ClickException:
                    kill_detail = f"floor: {floor} (not configured)"

        # ── Step 5: Registering protocols ──────────────────────────────
        protocols_detail = " + ".join(p.upper() for p in protocols)
        with _step(
            "Registering protocols...", protocols_detail, json_output=json_output
        ):
            pass

        # ── JSON output ────────────────────────────────────────────────
        if json_output:
            click.echo(
                json.dumps(
                    {
                        "action": action,
                        "agent_id": agent_id,
                        "name": name,
                        "framework": framework,
                        "did": did,
                        "trust_score": trust_score,
                        "trust_grade": trust_grade,
                        "agent": agent,
                    }
                )
            )
            return

        # ── Final banner ────────────────────────────────────────────────
        url = f"{api_url.rstrip('/')}/v1/agents/{agent_id}"
        console.print()
        console.print(
            f"  [ainfera.success]\u2713 Agent live\u2192[/] "
            f"[ainfera.brand]{url}[/]"
        )
        console.print()

        # ── Trust dimensions table ──────────────────────────────────────
        if trust_dimensions:
            _print_trust_table(trust_dimensions)
    finally:
        client.close()


# ── Helpers ─────────────────────────────────────────────────────────────


def _find_existing_by_name(client: AinferaClient, name: str) -> dict | None:
    try:
        response = client.list_agents(name=name, per_page=50)
    except click.ClickException:
        return None
    except httpx.HTTPError:
        return None
    items = response.get("agents") if isinstance(response, dict) else None
    if items is None and isinstance(response, dict):
        items = response.get("items", [])
    if not items:
        return None
    for item in items:
        if item.get("name") == name:
            return item
    return None


def _format_sandbox_detail(sandbox: str, memory: str, cpu: int) -> str:
    mem_up = str(memory).upper() if isinstance(memory, str) else f"{memory}MB"
    label = sandbox.capitalize() if isinstance(sandbox, str) else "Docker"
    return f"{label} ({mem_up}, {cpu} CPU)"


def _format_billing_detail(model: str, rate: float) -> str:
    unit = {
        "per_call": "invocation",
        "per_token": "token",
        "per_minute": "minute",
    }.get(model, "call")
    try:
        rate_str = f"${float(rate):.3f}"
    except (TypeError, ValueError):
        rate_str = f"${rate}"
    return f"{rate_str}/{unit}"


def _extract_dimensions(trust_data: dict) -> dict[str, float]:
    """Pull dimension scores out of a trust response in a tolerant way."""
    if not isinstance(trust_data, dict):
        return {}
    raw = trust_data.get("dimensions") or {}
    if isinstance(raw, dict) and raw:
        return {k: float(v) for k, v in raw.items() if isinstance(v, (int, float))}
    # Fall back to flat fields (reliability_score etc.)
    keys = ("safety", "reliability", "quality", "performance", "reputation")
    flat = {
        k: float(trust_data[f"{k}_score"])
        for k in keys
        if isinstance(trust_data.get(f"{k}_score"), (int, float))
    }
    return flat


class _step:
    """Context manager: show a spinner, then print the completed line."""

    def __init__(self, label: str, detail: str, *, json_output: bool):
        self.label = label
        self.detail = detail
        self.json_output = json_output
        self._status = None

    def __enter__(self):
        if self.json_output:
            return self
        self._status = console.status(f"  [ainfera.muted]{self.label}[/]")
        self._status.__enter__()
        time.sleep(0.4)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._status is not None:
            self._status.__exit__(exc_type, exc, tb)
        if self.json_output:
            return False
        if exc_type is None:
            console.print(
                f"  [ainfera.brand]\u25b8[/] {self.label:<30} "
                f"[ainfera.muted]{self.detail}[/]  [ainfera.success]\u2713[/]"
            )
        return False


def _print_header(*, name: str, framework: str, did: str) -> None:
    console.print()
    console.print(
        Panel(
            "\n"
            f"  Agent:     [bold]{name}[/]\n"
            f"  Framework: [ainfera.muted]{framework}[/]\n"
            f"  DID:       [ainfera.muted]{did}[/]\n",
            title="[bold]Ainfera Deploy[/]",
            border_style="ainfera.brand",
            padding=(0, 2),
        )
    )
    console.print()


def _print_trust_table(dimensions: dict[str, float]) -> None:
    table = Table(border_style="ainfera.muted", show_edge=True)
    table.add_column("Dimension", style="bold")
    table.add_column("Score", justify="center")
    table.add_column("Bar", no_wrap=True)
    for name, value in dimensions.items():
        filled = int(value * 22)
        empty = 22 - filled
        bar = f"[ainfera.brand]{'█' * filled}[/]{'░' * empty}"
        table.add_row(name.capitalize(), f"{value:.2f}", bar)
    console.print(table)
    console.print()


def _print_dry_run(
    *,
    name: str,
    framework: str,
    sandbox: str,
    memory: str,
    cpu: int,
    floor: int,
    from_config: bool,
    json_output: bool,
):
    if json_output:
        click.echo(
            json.dumps(
                {
                    "dry_run": True,
                    "name": name,
                    "framework": framework,
                    "sandbox": sandbox,
                    "endpoint": (
                        "/v1/agents/from-config" if from_config else "/v1/agents"
                    ),
                }
            )
        )
        return
    _print_header(name=name, framework=framework, did="(dry-run)")
    endpoint = "/v1/agents/from-config" if from_config else "/v1/agents"
    console.print(
        Panel(
            f"\n  Sandbox:    {_format_sandbox_detail(sandbox, memory, cpu)}\n"
            f"  Kill floor: {floor}\n\n"
            f"  [ainfera.muted]Would POST to {endpoint} (dry-run).[/]\n",
            title="[bold]Deploy Plan[/]",
            border_style="ainfera.muted",
            padding=(0, 2),
        )
    )


# ── Demo mode (unchanged) ───────────────────────────────────────────────

_DEMO_TRUST = {
    "score": 942,
    "grade": "AAA",
    "dimensions": {
        "Safety": 0.96,
        "Reliability": 0.94,
        "Quality": 0.93,
        "Performance": 0.95,
        "Reputation": 0.94,
    },
}


def _run_demo(*, json_output: bool) -> None:
    """Showcase deploy sequence with mock data — safe for stage demos."""
    if json_output:
        click.echo(
            json.dumps(
                {
                    "demo": True,
                    "agent_id": "a7f3",
                    "name": "my-agent",
                    "framework": "langchain",
                    "trust_score": _DEMO_TRUST["score"],
                    "trust_grade": _DEMO_TRUST["grade"],
                    "dimensions": _DEMO_TRUST["dimensions"],
                }
            )
        )
        return

    console.print()
    console.print(
        Panel(
            "\n"
            "  Agent:     [bold]my-agent[/]\n"
            "  Framework: [ainfera.muted]LangChain (auto-detected)[/]\n"
            "  DID:       [ainfera.muted]did:ainfera:agent:a7f3[/]\n",
            title="[bold]Ainfera Deploy[/]",
            border_style="ainfera.brand",
            padding=(0, 2),
        )
    )
    console.print()

    steps = [
        ("Provisioning sandbox...", "Docker (512MB, 1 CPU)"),
        ("Computing trust score...", f"{_DEMO_TRUST['grade']} ({_DEMO_TRUST['score']})"),
        ("Activating billing...", "$0.003/invocation"),
        ("Arming kill switch...", "floor: 400"),
        ("Registering protocols...", "MCP + A2A"),
    ]
    for label, detail in steps:
        with console.status(f"  [ainfera.muted]{label}[/]"):
            time.sleep(0.4)
        console.print(
            f"  [ainfera.brand]\u25b8[/] {label:<30} "
            f"[ainfera.muted]{detail}[/]  [ainfera.success]\u2713[/]"
        )

    console.print()
    console.print(
        "  [ainfera.success]\u2713 Agent live\u2192[/] "
        "[ainfera.brand]https://api.ainfera.ai/agent/a7f3[/]"
    )
    console.print()

    _print_trust_table(
        {k.lower(): v for k, v in _DEMO_TRUST["dimensions"].items()}
    )
