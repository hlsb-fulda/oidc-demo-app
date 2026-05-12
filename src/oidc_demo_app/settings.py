from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class ProviderSettings(BaseModel):
    issuer: str
    client_id: str
    client_secret: str

    display_name: str
    display_icon: str = "bi-person-circle"

    scopes: list[str] = Field(default_factory=lambda: ["openid", "profile", "email"])
    audience: str = Field(default_factory=lambda other: other["client_id"])


class AppSettings(BaseSettings):
    base_url: str = "http://localhost:8000"

    providers: dict[str, ProviderSettings] = {}

    model_config = SettingsConfigDict(
        toml_file="config.toml",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)


settings = AppSettings()
