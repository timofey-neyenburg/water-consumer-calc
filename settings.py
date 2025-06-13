from enum import Enum
import logging
import logging.config
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppMode(Enum):
    DEV = "dev"
    BUILD = "build"

class AppSettings(BaseSettings):
    MODE: AppMode = AppMode.DEV

    model_config = SettingsConfigDict(
        extra="allow",
        env_file=Path(__file__).parent / ".env"
    )

    @property
    def ROOT_FOLDER(self) -> Path | str:
        if self.MODE == AppMode.DEV:
            return Path(__file__).parent
        else:
            return "./_internal"

    @property
    def ASSETS_FOLDER(self) -> Path | str:
        print(self.MODE)
        if self.MODE == AppMode.DEV:
            if os.name == 'nt':
                return ".\\water-calc-assets"
            else:
                return "./water-calc-assets"
        else:
            if os.name == "nt":
                return ".\\_internal\\assets"
            else:
                return "./_internal/assets"

    @property
    def TEX_COMPILER_DIR(self) -> str:
        if self.MODE == AppMode.DEV:
            if os.name == 'nt':
                return ".\\water-calc-assets\\miktex\\texmfs\\install\\miktex\\bin\\x64\\"
            else:
                raise OSError("Operating system doesnt support this latex compiler")
        else:
            if os.name == "nt":
                return ".\\_internal\\assets\\miktex\\texmfs\\install\\miktex\\bin\\x64\\"
            else:
                raise OSError("Operating system doesnt support this latex compiler")
    
    @property
    def TEX_COMPILER_BIN(self) -> str:
        return os.path.join(self.TEX_COMPILER_DIR, "pdflatex.exe")



CONF = AppSettings()

# Определение конфигурации логгера
LOGGING_CONFIG = {""
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s - '
                      '[%(filename)s:%(lineno)d]'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'DEBUG'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join('logs', 'app.log'),
            'formatter': 'detailed',
            'level': 'DEBUG'
        },
        'error_file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join('logs', 'errors.log'),
            'formatter': 'detailed',
            'level': 'WARNING'
        }
    },
    'loggers': {
        'app': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True
        },
        'errors': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False
        }
    }
}

# Создание директории для логов, если она не существует
if not os.path.exists('logs'):
    os.makedirs('logs')

# Применение конфигурации
logging.config.dictConfig(LOGGING_CONFIG)

# Пример использования
app_logger = logging.getLogger('app')
error_logger = logging.getLogger('errors')

app_logger.debug("configured loggers")
app_logger.debug(CONF)
app_logger.debug(str(Path(__file__).parent))
