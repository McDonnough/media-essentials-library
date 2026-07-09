from .app import MediaEssentialsLibraryApp
from .logging_config import configure_logging


def main() -> None:
    configure_logging()
    MediaEssentialsLibraryApp().run()


if __name__ == "__main__":
    main()
