"""Ainfera Python SDK.

A typed, synchronous wrapper around the Ainfera platform API. Shares the
CLI's HTTP client so every request is governed by the same auth,
timeouts, error handling, and User-Agent.

    from ainfera.sdk import AinferaSDK

    sdk = AinferaSDK(api_key="ainf_...")
    agent = sdk.create_agent(name="my-agent", framework="langchain")
    trust = sdk.get_trust_score(agent["id"])
"""

from ainfera.sdk.client import AinferaSDK

__all__ = ["AinferaSDK"]
