"""ainfera.yaml schema, parser, and generator."""

from __future__ import annotations

from typing import Literal

import yaml
from pydantic import BaseModel, Field


class ComputeConfig(BaseModel):
    sandbox: Literal["docker", "firecracker"] = "docker"
    memory: str = "512mb"
    cpu: int = 1
    timeout: str = "300s"


class TrustConfig(BaseModel):
    dimensions: dict[str, bool] = Field(
        default_factory=lambda: {
            "reliability": True,
            "security": True,
            "quality": True,
        }
    )
    anomaly_detection: bool = True
    quarantine_threshold: int = 400


class BillingConfig(BaseModel):
    enabled: bool = True
    model: Literal["per_call", "per_token", "per_minute"] = "per_call"
    price_per_call: float = 0.003
    currency: str = "usd"
    creator_share: float = 0.80


class InferenceConfig(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    fallback: str | None = None


class KillSwitchConfig(BaseModel):
    enabled: bool = True
    auto_quarantine: bool = True
    budget_limit: float | None = None


class AinferaConfig(BaseModel):
    name: str
    framework: str
    version: str = "0.1.0"
    compute: ComputeConfig = ComputeConfig()
    trust: TrustConfig = TrustConfig()
    billing: BillingConfig = BillingConfig()
    inference: InferenceConfig = InferenceConfig()
    kill_switch: KillSwitchConfig = KillSwitchConfig()


# Section comments injected into generated YAML
_SECTION_COMMENTS = {
    "compute": "# Sandbox settings (docker for dev, firecracker at scale)",
    "trust": "# Trust scoring thresholds",
    "billing": "# Billing model (per_call, per_token, per_minute)",
    "inference": "# LLM provider routing",
    "kill_switch": "# Kill switch auto-quarantines misbehaving agents",
}


def generate_yaml(config: AinferaConfig) -> str:
    """Render config to YAML string with helpful comments."""
    data = config.model_dump(exclude_none=True)
    raw = yaml.safe_dump(data, default_flow_style=False, sort_keys=False)

    # Inject section comments
    lines = raw.splitlines()
    result: list[str] = []
    for line in lines:
        key = line.split(":")[0].strip() if ":" in line else ""
        if key in _SECTION_COMMENTS and not line.startswith(" "):
            result.append("")
            result.append(_SECTION_COMMENTS[key])
        result.append(line)

    return "\n".join(result).strip() + "\n"


def parse_yaml(yaml_string: str) -> AinferaConfig:
    """Parse ainfera.yaml string into config object."""
    data = yaml.safe_load(yaml_string)
    return AinferaConfig(**data)


def load_yaml_file(path: str = "ainfera.yaml") -> AinferaConfig:
    """Load and parse ainfera.yaml from a file path."""
    with open(path) as f:
        return parse_yaml(f.read())
