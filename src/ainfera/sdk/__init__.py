"""Internal SDK helper for the ainfera CLI.

Shares the CLI's HTTP client so every request is governed by the same
auth, timeouts, error handling, and User-Agent. External callers should
use the separately-published ``ainfera-sdk`` package.
"""

from ainfera.sdk.client import AinferaSDK

__all__ = ["AinferaSDK"]
