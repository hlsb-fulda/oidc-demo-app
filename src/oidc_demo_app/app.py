import datetime
import json
import logging
import os
from typing import Any

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starsessions import InMemoryStore, SessionAutoloadMiddleware, SessionMiddleware

from oidc_demo_app.oidc import build_auth, unsafe_parse_token
from oidc_demo_app.settings import settings

logger = logging.getLogger(__name__)


def create_app() -> Starlette:
    oauth = build_auth()

    templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

    templates.env.globals["settings"] = settings
    templates.env.globals["TIMESTAMP_CLAIMS"] = {
        "iat",
        "exp",
        "nbf",
        "auth_time",
        "updated_at",
    }
    templates.env.globals["STANDARD_CLAIMS"] = {
        "iss",
        "sub",
        "aud",
        "exp",
        "nbf",
        "iat",
        "jti",
        "azp",
        "nonce",
        "at_hash",
        "c_hash",
        "name",
        "given_name",
        "family_name",
        "middle_name",
        "nickname",
        "preferred_username",
        "profile",
        "picture",
        "website",
        "email",
        "email_verified",
        "gender",
        "birthdate",
        "zoneinfo",
        "locale",
        "phone_number",
        "phone_number_verified",
        "address",
        "updated_at",
        "acr",
        "amr",
        "sid",
        "auth_time",
        "typ",
        "alg",
        "kid",
        "use",
        "scope",
        "active",
        "client_id",
        "username",
        "token_type",
    }

    def filter_ts(value: Any) -> str:
        if not isinstance(value, (int, float)):
            return str(value)
        return datetime.datetime.fromtimestamp(value, tz=datetime.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    def filter_tojson(value: Any) -> str:
        return json.dumps(value, indent=2, default=str)

    templates.env.filters["ts"] = filter_ts
    templates.env.filters["tojson"] = filter_tojson

    async def index(request: Request):
        if request.session.get("token"):
            return RedirectResponse(request.url_for("info"))
        else:
            return RedirectResponse(request.url_for("login"))

    async def login(request: Request):
        if request.session.get("token"):
            return RedirectResponse(request.url_for("info"))

        return templates.TemplateResponse(
            request,
            "login.html.j2",
            {
                "request": request,
                "providers": settings.providers,
            },
        )

    async def login_redirect(request: Request):
        provider = request.path_params["provider"]
        if provider not in settings.providers:
            raise HTTPException(404, f"Unknown provider: {provider!r}")

        client = oauth.create_client(provider)

        return await client.authorize_redirect(
            request,
            request.url_for("login_callback", provider=provider),
        )

    async def login_callback(request: Request):
        provider = request.path_params["provider"]
        if provider not in settings.providers:
            raise HTTPException(404, f"Unknown provider: {provider!r}")

        error = request.query_params.get("error")
        if error:
            return templates.TemplateResponse(
                request,
                "error.html.j2",
                {
                    "request": request,
                    "message": request.query_params.get("error_description", error),
                },
                status_code=400,
            )

        client = oauth.create_client(provider)

        try:
            token = await client.authorize_access_token(request)
        except Exception as ex:
            logger.warning("Access token authorization failed: %s", ex)
            return templates.TemplateResponse(
                request,
                "error.html.j2",
                {
                    "request": request,
                    "message": str(ex),
                },
                status_code=400,
            )

        request.session["provider"] = provider
        request.session["token"] = token

        return RedirectResponse(request.url_for("info"), status_code=302)

    async def logout(request: Request):
        provider = request.session.get("provider")
        token = request.session.get("token")
        if not token:
            return RedirectResponse(request.url_for("login"))

        client = oauth.create_client(provider)
        url = await client.create_logout_url(
            post_logout_redirect_uri=str(request.url_for("index")),
            client_id=settings.providers[provider].client_id,
            id_token_hint=token["id_token"],
        )

        request.session.clear()

        return RedirectResponse(url["url"] if url else request.url_for("index"))

    async def info(request: Request):
        provider = request.session.get("provider")
        token = request.session.get("token")
        if not token:
            return RedirectResponse(request.url_for("login"))

        client = oauth.create_client(provider)
        discovery = await client.load_server_metadata()

        try:
            user = await client.parse_id_token(token, nonce=None)
        except Exception:
            del request.session["token"]
            return RedirectResponse(request.url_for("login"))

        id_token = unsafe_parse_token(token["id_token"])
        access_token = unsafe_parse_token(token["access_token"])

        userinfo = await client.userinfo(token=token)

        if "introspection_endpoint" in discovery:
            introspection = (
                await client.post(
                    discovery["introspection_endpoint"],
                    token=token,
                    data={
                        "token": token["access_token"],
                        "token_hint": "access_token",
                        "client_id": settings.providers[provider].client_id,
                        "client_secret": settings.providers[provider].client_secret,
                    },
                )
            ).json()
        else:
            introspection = None

        jwks_doc = await client.fetch_jwk_set()

        return templates.TemplateResponse(
            request,
            "info.html.j2",
            {
                "request": request,
                "provider": settings.providers[provider],
                "token": token,
                "user": user,
                "id_token": id_token,
                "access_token": access_token,
                "userinfo": userinfo,
                "introspection": introspection,
                "discovery": discovery,
                "jwks_doc": jwks_doc,
            },
        )

    routes = [
        Mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static"),
        Mount(
            "/",
            routes=[
                Route("/", endpoint=index, name="index"),
                Route("/login", endpoint=login, name="login"),
                Route("/login/{provider:str}", endpoint=login_redirect, name="login_redirect"),
                Route("/login/{provider:str}/callback", endpoint=login_callback, name="login_callback"),
                Route("/logout", endpoint=logout, name="logout"),
                Route("/info", endpoint=info, name="info"),
            ],
            middleware=[
                Middleware(SessionMiddleware, store=InMemoryStore()),
                Middleware(SessionAutoloadMiddleware),
            ],
        ),
    ]

    return Starlette(routes=routes)


app = create_app()
