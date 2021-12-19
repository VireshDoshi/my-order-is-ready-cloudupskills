import structlog
from structlog.dev import set_exc_info, ConsoleRenderer
from structlog.processors import StackInfoRenderer, TimeStamper, add_log_level

def config_structlog():
    structlog.configure_once(
        processors=[
            add_log_level,
            StackInfoRenderer(),
            set_exc_info,
            TimeStamper(fmt="%Y-%m-%d %H:%M.%S", utc=False),
            ConsoleRenderer(),
        ]
    )
