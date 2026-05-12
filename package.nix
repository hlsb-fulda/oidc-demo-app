{ python3
, ...
}:

python3.pkgs.buildPythonApplication {
  name = "oidc-demo-app";

  src = ./.;

  pyproject = true;

  build-system = [ python3.pkgs.uv-build ];

  dependencies = with python3.pkgs; [
    click
    fastapi
    starlette
    starsessions
    authlib
    httpx
    itsdangerous
    uvicorn
    pyyaml
    jinja2
    pydantic
    pydantic-settings
  ]
  ++ uvicorn.optional-dependencies.standard;

  # Has no tests
  doCheck = false;
}
