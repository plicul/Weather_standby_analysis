from PySide6.QtSql import QSqlDatabase
import logging
import os

logger = logging.getLogger("logger")


def connectToDatabase():
    database = QSqlDatabase.addDatabase("QSQLITE")
    if not database.isValid():
        logger.error("Cannot add database")
        return False

    relative_path = os.path.join(os.path.dirname(__file__), 'diplDB')
    database.setDatabaseName(relative_path)

    if not database.open():
        logger.error("Cannot open database")
        return False

    logger.info("Database connected")
    return True