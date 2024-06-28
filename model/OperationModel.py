from PySide6.QtSql import QSqlDatabase, QSqlQuery
import logging
from typing import List

from consts.types import Operation
from model.LimitModel import LimitModel

logger = logging.getLogger("logger")


class OperationModel:
    def __init__(self, db=QSqlDatabase()):
        self.db = db

    def selectOperation(self, operationId, limitModel: LimitModel) -> Operation | None:
        query = QSqlQuery(self.db)
        query.prepare("SELECT Ship_Dir,Time_Req,Type,[Limit] FROM Operation WHERE Id = :operationId")
        query.bindValue(":operationId", operationId)

        if not query.exec():
            logger.error(f"Query Error: {query.lastError().text()}")
            return None

        query.next()

        return Operation(
            id=operationId,
            shipDir=query.value(0),
            timeReq=query.value(1),
            type=query.value(2),
            limit=limitModel.selectLimit(query.value(3))
        )

    def getAllOperations(self) -> List[Operation | None]:
        query = QSqlQuery(self.db)
        query.prepare("SELECT Id FROM Operation")

        if not query.exec():
            logger.error(f"Query Error: {query.lastError().text()}")
            return []

        operations = []
        while query.next():
            operationId = query.value(0)
            operation = self.selectOperation(operationId)
            if operation:
                operations.append(operation)

        return operations

    def insertOperation(self, operation: Operation) -> bool:
        query = QSqlQuery(self.db)
        query.prepare("INSERT INTO Operation(time_req, ship_dir, type, [limit]) VALUES (?,?,?,?)")
        query.addBindValue(operation.timeReq)
        query.addBindValue(operation.shipDir)
        query.addBindValue(operation.type)
        query.addBindValue(operation.limit.id)

        if not query.exec():
            logger.error(f"Insert Error (Operation): {query.lastError().text()}")
            return False

        return True
