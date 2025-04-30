import logging
import logging.config
import os

# Определение конфигурации логгера
LOGGING_CONFIG = {
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