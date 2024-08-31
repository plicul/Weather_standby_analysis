from PySide6.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
import logging
from dataclasses import dataclass
from typing import List

from consts.types import LimitValue, Limit

logger = logging.getLogger("logger")


class LimitModel:
    def __init__(self, db=QSqlDatabase()):
        self.db = db

    def selectLimit(self, limitId) -> Limit | None:
        query = QSqlQuery(self.db)
        query.prepare("SELECT a.name, b.Wave_Period, b.Wave_Dir, b.Wave_Height FROM [Limit] as a left join Limit_Values as b on a.id = b.Limit_Id WHERE Limit_Id = :limitId")
        query.bindValue(":limitId", limitId)

        if not query.exec():
            logger.error(f"Query Error: {query.lastError().text()}")
            return None

        values = []
        name = ""
        while query.next():
            name = query.value(0)
            values.append(LimitValue(
                wavePeriod=query.value(1),
                waveDir=query.value(2),
                waveHeight=query.value(3)
            ))

        return Limit(id=limitId,name=name, values=values)

    def getAllLimits(self) -> List[Limit | None]:
        query = QSqlQuery(self.db)
        query.prepare("SELECT Id FROM [Limit]")

        if not query.exec():
            logger.error(f"Query Error: {query.lastError().text()}")
            return []

        limits = []
        while query.next():
            limitId = query.value(0)
            limit = self.selectLimit(limitId)
            if limit:
                limits.append(limit)

        return limits

    def insertLimit(self, limit: Limit) -> bool:
        query = QSqlQuery(self.db)
        if limit.id == -1:
            query.prepare("SELECT Max(Id)+1 FROM [Limit]")
            query.exec()
            query.next()
            limit.id = query.value(0) or 1

        query.prepare("INSERT INTO [Limit] (Id) VALUES (?)")
        query.addBindValue(limit.id)

        if not query.exec():
            logger.error(f"Insert Error (Limit): {query.lastError().text()}")
            return False

        for value in limit.values:
            if not self.insertLimitValue(limit.id, value):
                return False

        return True

    def insertLimitValue(self, limitId, value: LimitValue) -> bool:
        query = QSqlQuery(self.db)
        query.prepare("INSERT INTO Limit_Values (Limit_Id, Wave_Period, Wave_Dir, Wave_Height) VALUES (?, ?, ?, ?)")
        query.addBindValue(limitId)
        query.addBindValue(value.wavePeriod)
        query.addBindValue(value.waveDir)
        query.addBindValue(value.waveHeight)

        if not query.exec():
            logger.error(f"Insert Error (LimitValue): {query.lastError().text()}")
            return False

        return True
