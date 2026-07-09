from __future__ import annotations

import atexit
import logging
import sys
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path

from media_essentials_library.paths import get_app_config_dir

LOG_FILE_NAME = "media-essentials-library.log"


def get_log_path() -> Path:
    return get_app_config_dir() / LOG_FILE_NAME


def configure_logging() -> Path:
    log_path = get_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[
            RotatingFileHandler(
                log_path,
                maxBytes=1_000_000,
                backupCount=3,
                encoding="utf-8",
            )
        ],
        force=True,
    )

    sys.excepthook = log_uncaught_exception
    threading.excepthook = log_uncaught_thread_exception
    atexit.register(shutdown_logging)

    logging.getLogger(__name__).info("Logging initialized at %s", log_path)
    return log_path


def shutdown_logging() -> None:
    logging.shutdown()


def log_uncaught_exception(
    exception_type: type[BaseException],
    exception: BaseException,
    traceback,
) -> None:
    logging.getLogger(__name__).critical(
        "Uncaught exception",
        exc_info=(exception_type, exception, traceback),
    )
    sys.__excepthook__(exception_type, exception, traceback)


def log_uncaught_thread_exception(args: threading.ExceptHookArgs) -> None:
    logging.getLogger(__name__).critical(
        "Uncaught thread exception",
        exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
    )
    threading.__excepthook__(args)
