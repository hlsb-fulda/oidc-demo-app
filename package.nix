{ python3
, ...
}:

python3.pkgs.buildPythonApplication (finalAttrs: {
  name = "oidc-demo-app";

  src = ./.;

  pyproject = true;

  build-system = [ python3.pkgs.uv-build ];

  dependencies = with python3.pkgs; [
    click
    starlette
    starsessions
    authlib
    joserfc
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

  passthru = {
    python = python3;
    pythonPath = python3.pkgs.makePythonPath finalAttrs.passthru.dependencies;
  };
})
