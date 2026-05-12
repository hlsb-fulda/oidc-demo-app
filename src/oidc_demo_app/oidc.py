import logging
from typing import Any, TypedDict

from authlib.integrations.starlette_client import OAuth
from joserfc.util import json_b64decode

from oidc_demo_app.settings import settings

logger = logging.getLogger(__name__)


def build_auth() -> OAuth:
    oauth = OAuth()

    for key, provider in settings.providers.items():
        oauth.register(
            name=key,
            server_metadata_url=f"{provider.issuer.rstrip('/')}/.well-known/openid-configuration",
            client_id=provider.client_id,
            client_secret=provider.client_secret,
            client_kwargs={
                "scope": " ".join(provider.scopes),
            },
        )

        logger.info("Register OIDC provider: %r", key)

    return oauth


class TokenParts(TypedDict):
    header: dict[str, Any]
    payload: dict[str, Any]
    signature: str


def unsafe_parse_token(t: str) -> TokenParts | None:
    parts = t.split(".")
    if len(parts) != 3:
        return None

    (header, payload, signature) = parts

    header = json_b64decode(header.encode())
    payload = json_b64decode(payload.encode())

    return TokenParts(
        header=header,
        payload=payload,
        signature=signature,
    )
