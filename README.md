# OIDC Demo Resource Server
 
A minimal, modern OIDC client / resource server built.
Implements the Authorization Code Flow against any standards-compliant OpenID Connect provider, with a clean token inspection UI for development and debugging.
 
## Features

- **Multiple providers**: configure any number of OIDC providers simultaneously (Keycloak, Microsoft Entra, Google, Dex, …)
- **OIDC discovery**: fetches `/.well-known/openid-configuration` at startup; all endpoint URLs resolved automatically
- **Full Authorization Code Flow**: state and nonce generated and validated by authlib; id_token signature and claims verified on every login
- **Token inspection UI**: details page showing decoded claims, user info, introspection, and almost all details about the active session and authentication server:
  - User Profile
  - ID Token
  - Access Token
  - UserInfo
  - Token Introspection
  - Discovery
  - JWK Set

## Requirements
 
- Python ≥ 3.11
- [uv](https://docs.astral.sh/uv/) (`pip install uv`)

## Quick Start
 
```bash
# 1. Clone and enter the project
git clone <repo-url>
cd oidc-demo-app
 
# 2. Create your configuration
cp config.example.yaml config.yaml
$EDITOR config.yaml
 
# 3. Install dependencies
uv sync
 
# 4. Run
uv run oidc-demo-app
```
 
Open <http://localhost:8000>.

## Configuration
 
All configuration lives in `config.toml`.

### Provider fields
 
| Field           | Required | Default                    | Description                                               |
|-----------------|----------|----------------------------|-----------------------------------------------------------|
| `display_name`  | ✓        | -                          | Display name shown on the login page                      |
| `display_icon`  |          | `bi-person-circle`         | [Bootstrap Icons](https://icons.getbootstrap.com/) class  |
| `issuer`        | ✓        | -                          | OIDC issuer URL (discovery appended automatically)        |
| `client_id`     | ✓        | -                          | OAuth2 client ID                                          |
| `client_secret` | ✓        | -                          | OAuth2 client secret                                      |
| `scopes`        |          | `[openid, profile, email]` | Scopes to request                                         |
| `audience`      |          | `client_id`                | JWT audience override (rarely needed)                     |

### Redirect URIs
 
Register the following redirect URI at each identity provider:

```
{base_url}/login/{provider_key}/callback

# Examples:
http://localhost:8000/login/test/callback
http://localhost:8000/login/other/callback
```

## Development
 
```bash
# Install with dev dependencies
uv sync
 
# Run with auto-reload
RELOAD=true uv run oidc-demo-app
 
# Lint
uv run ruff check src/
uv run ruff format src/
```

## Production

```bash
uv run uvicorn oidc_demo_app.app:app
```
