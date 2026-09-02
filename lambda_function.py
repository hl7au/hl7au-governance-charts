"""AWS Lambda handler for the parameterised endpoints (Function URL or API Gateway v2).

Deployed as the origin behind the CloudFront `/render/*` behaviour. The static
`/charts/*` objects in S3 cover the fixed URLs; this covers everything with a
query string.

The model is parsed once per container and reused across invocations.
"""
from __future__ import annotations

import os
from pathlib import Path

from src.service import Renderer

SOURCE = Path(os.environ.get("GOVERNANCE_MD", Path(__file__).parent / "governance.md"))
_renderer = Renderer(SOURCE)


def handler(event, context=None):  # noqa: ANN001 - AWS signature
    request = event.get("requestContext", {}).get("http", {})
    path = request.get("path") or event.get("rawPath", "/")
    query = event.get("rawQueryString", "") or ""
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}

    response = _renderer.handle(path, query,
                                if_none_match=headers.get("if-none-match"))
    return {
        "statusCode": response.status,
        "headers": response.headers(),
        "body": response.body,
        "isBase64Encoded": False,
    }
