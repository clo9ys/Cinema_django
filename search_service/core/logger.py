import logging
import os
from pathlib import Path

# путь к папке с логами
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

def setup_logger(name="cinema"):
    """настраивает и возвращает логгер"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # формат записи: уровень время модуль сообщение
    formatter = logging.Formatter(
        fmt="%(levelname)s %(asctime)s %(module)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # вывод в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # вывод в файл
    file_handler = logging.FileHandler(LOGS_DIR / "search.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# создаем основной логгер для импорта
logger = setup_logger()
