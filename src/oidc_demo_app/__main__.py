import click


@click.command()
@click.option("-h", "--host", default="127.0.0.1", help="Host to server")
@click.option("-p", "--port", default=8000, type=int, help="Port to server")
@click.option("-v", "--verbose", default=0, count=True, help="Increase verbosity")
def main(host, port, verbose) -> None:
    import uvicorn

    log_level = ["warning", "info", "debug", "trace"][min(verbose, 3)]

    uvicorn.run(
        "oidc_demo_app.app:app",
        host=host,
        port=port,
        reload=True,
        log_level=log_level,
    )


if __name__ == "__main__":
    main()
