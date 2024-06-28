from PySide6.QtSql import QSqlTableModel, QSqlDatabase
import logging

from consts.types import SeaData, OperationResult, Operation, LimitValue

logger = logging.getLogger("logger")


def getRelativeDir(waveDir, shipDir):
    relativeDir = (waveDir - shipDir) % 360
    if relativeDir < 0:
        relativeDir += 360
    return relativeDir


def findClosestWaveDir(limitVals: list[LimitValue], relativeDir: float, wavePeriod: int) -> LimitValue:
    closestLimit = min(limitVals, key=lambda lv: abs(lv.waveDir - relativeDir) if lv.wavePeriod == wavePeriod else 1000)
    return closestLimit


def limitCheck(waveHeight, waveDir, shipDir, values, wavePeriod):
    relativeDir = getRelativeDir(waveDir, shipDir)
    closestLimit = findClosestWaveDir(limitVals=values, relativeDir=relativeDir, wavePeriod=wavePeriod)
    if closestLimit.waveHeight < waveHeight:
        return False
    return True


class OperationResultModel(QSqlTableModel):
    def __init__(self, parent=None, db=QSqlDatabase()):
        super(OperationResultModel, self).__init__(parent, db)
        self.setTable("Operation_Result")
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)
        if not self.select():
            logger.error(f"Error: {self.lastError().text()}")
        else:
            logger.info("Model(Operation_Result) created and data selected successfully")

    def selectRow(self, row) -> OperationResult:
        record = self.record(row)
        operationResult = OperationResult(
            operationId=record.value("Operation_Id"),
            year=record.value("Year"),
            month=record.value("Month"),
            day=record.value("Day"),
            hour=record.value("Hour"),
            success=record.value("Success")
        )
        return operationResult

    def getAllRows(self) -> list[OperationResult]:
        rows = []
        for row in range(self.rowCount()):
            rows.append(self.selectRow(row))
        return rows

    def insertRowData(self, operationResult: OperationResult) -> bool:
        row = self.rowCount()
        self.insertRow(row)
        self.setData(self.index(row, self.fieldIndex("Operation_Id")), operationResult.operationId)
        self.setData(self.index(row, self.fieldIndex("Year")), operationResult.year)
        self.setData(self.index(row, self.fieldIndex("Month")), operationResult.month)
        self.setData(self.index(row, self.fieldIndex("Day")), operationResult.day)
        self.setData(self.index(row, self.fieldIndex("Hour")), operationResult.hour)
        self.setData(self.index(row, self.fieldIndex("Success")), operationResult.success)
        if not self.submitAll():
            logger.error(f"Insert Error: {self.lastError().text()}")
            return False
        logger.info("Row inserted successfully")
        return True

    def generateOperationResults(self, seaDataList: list[SeaData], operation: Operation):
        for seaData in seaDataList:
            operationResult = OperationResult(
                operationId=operation.id,
                year=seaData.year,
                month=seaData.month,
                day=seaData.day,
                hour=seaData.hour,
                success=limitCheck(seaData.waveHeight, seaData.waveDir, operation.shipDir, operation.limit.values,
                                   seaData.wavePeriod)
            )
            self.insertRowData(operationResult)
        return
