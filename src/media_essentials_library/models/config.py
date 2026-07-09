from dataclasses import dataclass


@dataclass
class PlexServerConfig:
    language: str = "en"
    date_format: str = "iso"
    server_url: str = ""
    token: str = ""
