import logging
from datetime import datetime
from sys import exc_info

# Настройка основного логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Устанавливаем минимальный уровень логирования

# Создаем форматтер
formatter = logging.Formatter(
  '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  datefmt='%Y-%m-%d %H:%M:%S'
)

# Добавляем обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def log_event(user_id: int, event_type: str, details: str = "", exc_info=None):

  try:
    log_message = f"UserID={user_id} | Event={event_type}"
    if details:
      log_message += f" | Details={details}"

    if exc_info:
      logger.error(log_message, exc_info=exc_info)
    else:
      logger.info(log_message)
  except Exception as e:
    logger.critical(f"Critical logging failure: {str(e)}", exc_info=True)