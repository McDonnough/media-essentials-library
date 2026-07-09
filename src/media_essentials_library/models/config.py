from dataclasses import dataclass


@dataclass
class PlexServerConfig:
    server_url: str = ""
    token: str = ""
    date_format: str = "iso"
