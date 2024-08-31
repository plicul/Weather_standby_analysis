import math
from datetime import timedelta, datetime
from typing import Optional

from PySide6.QtCore import QDate, QDateTime
from PySide6.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
import logging

from consts.types import SeaData, SimpleOperationResult, Operation, LimitValue, SeaDataDate, CampaignOperation, SimpleOperationResult

logger = logging.getLogger("logger")


def interpolateWavePeriod(smallerPeriodLimit: LimitValue, biggerPeriodLimit: LimitValue,
                          wavePeriod: float) -> LimitValue:
    if smallerPeriodLimit.wavePeriod == biggerPeriodLimit.wavePeriod:
        return LimitValue(wavePeriod, smallerPeriodLimit.waveDir, smallerPeriodLimit.waveHeight)

    proportion = ((wavePeriod - smallerPeriodLimit.wavePeriod) /
                  (biggerPeriodLimit.wavePeriod - smallerPeriodLimit.wavePeriod))
    interpolatedWaveHeight = (smallerPeriodLimit.waveHeight +
                              proportion * (biggerPeriodLimit.waveHeight - smallerPeriodLimit.waveHeight))
    waveDir = smallerPeriodLimit.waveDir

    return LimitValue(wavePeriod, waveDir, interpolatedWaveHeight)


def findClosestWaveDir(limitVals: list[LimitValue], relativeDir: float, wavePeriod: float) -> float:
    closestLimit = min(limitVals, key=lambda lv: abs(lv.waveDir - relativeDir))
    return closestLimit.waveDir


def findWaveHeightLimit(limitVals: list[LimitValue], relativeDir: float, wavePeriod: float) -> float:
    closestWaveDir = findClosestWaveDir(limitVals, relativeDir, wavePeriod)
    waveDirLimits = [limitVal for limitVal in limitVals if limitVal.waveDir == closestWaveDir]

    waveDirLimits.sort(key=lambda limitVal: limitVal.wavePeriod)
    smallerPeriodLimit: Optional[LimitValue] = None
    biggerPeriodLimit: Optional[LimitValue] = None
    for limitVal in waveDirLimits:
        if limitVal.wavePeriod <= wavePeriod:
            smallerPeriodLimit = limitVal
        if limitVal.wavePeriod >= wavePeriod and biggerPeriodLimit is None:
            biggerPeriodLimit = limitVal
            break
    if smallerPeriodLimit is None or biggerPeriodLimit is None:
        return -1

    interpolatedLimit = interpolateWavePeriod(smallerPeriodLimit, biggerPeriodLimit, wavePeriod)
    return interpolatedLimit.waveHeight


def getRelativeDir(waveDir: float, shipDir: float):
    relativeDir = (waveDir - shipDir) % 360
    return relativeDir
    #if relativeDir < 0:
    #    relativeDir += 360


def limitCheck(waveHeight: float, waveDir: float, wavePeriod: float, shipDir: float, limitVals: list[LimitValue]):
    relativeDir = getRelativeDir(waveDir, shipDir)
    waveHeightLimit = findWaveHeightLimit(limitVals=limitVals, relativeDir=relativeDir, wavePeriod=wavePeriod)
    if waveHeightLimit < waveHeight or waveHeightLimit == -1:
        return False
    return True


def successCheck(shipDir: float, limitVals: list[LimitValue], seaData: SeaData, operationType: str):
    if not limitCheck(seaData.waveHeight, seaData.waveDir, seaData.wavePeriod, shipDir, limitVals):
        return False
    return True


class SimpleOperationResultModel(QSqlTableModel):
    def __init__(self, parent=None, db=QSqlDatabase()):
        super(SimpleOperationResultModel, self).__init__(parent, db)
        self.setTable("Simple_Operation_Result")
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.db = db
        if not self.select():
            logger.error(f"Error: {self.lastError().text()}")
        else:
            logger.info("Model(Operation_Result) created and data selected successfully")

    def selectRow(self, row) -> SimpleOperationResult:
        record = self.record(row)
        simpleOperationResult = SimpleOperationResult(
            operationName= "",
            operationId=record.value("Operation_Id"),
            year=record.value("Year"),
            month=record.value("Month"),
            day=record.value("Day"),
            hour=record.value("Hour"),
            success=record.value("Success")
        )
        return simpleOperationResult

    def getAllRows(self) -> list[SimpleOperationResult]:
        query = QSqlQuery(self.db)
        query.prepare("SELECT  O.name,b.Operation_Id, b.year, b.month, b.day, b.hour, b.success FROM Simple_Operation_Result b left join Operation O on O.Id = b.Operation_Id order by year, Month, Day, Hour")

        if not query.exec():
            logger.error(f"Query Error: {query.lastError().text()}")
            return []

        rows = []
        while query.next():
            rows.append(SimpleOperationResult(query.value(0), query.value(1), query.value(2), query.value(3), query.value(4), query.value(5), query.value(6)))

        return rows

    def insertRowData(self, SimpleOperationResult: SimpleOperationResult) -> bool:
        row = self.rowCount()
        self.insertRow(row)
        self.setData(self.index(row, self.fieldIndex("Operation_Id")), SimpleOperationResult.operationId)
        self.setData(self.index(row, self.fieldIndex("Year")), SimpleOperationResult.year)
        self.setData(self.index(row, self.fieldIndex("Month")), SimpleOperationResult.month)
        self.setData(self.index(row, self.fieldIndex("Day")), SimpleOperationResult.day)
        self.setData(self.index(row, self.fieldIndex("Hour")), SimpleOperationResult.hour)
        self.setData(self.index(row, self.fieldIndex("Success")), SimpleOperationResult.success)
        if not self.submitAll():
            logger.error(f"Insert Error: {self.lastError().text()}")
            return False
        logger.info("Row inserted successfully")
        return True

    def generateOperationResults(self, seaDataList: list[SeaData], operation: Operation):
        SimpleOperationResults = []
        for seaData in seaDataList:
            simpleOperationResult = SimpleOperationResult(
                operationName="",
                operationId=operation.id,
                year=seaData.year,
                month=seaData.month,
                day=seaData.day,
                hour=seaData.hour,
                success=successCheck(operation.shipDir, operation.limit.values, seaData, operation.type)
            )
            SimpleOperationResults.append(simpleOperationResult)
            #self.insertRowData(SimpleOperationResult)
        self.insertRowDataQuery(SimpleOperationResults)
        return

    def insertRowDataQuery(self, SimpleOperationResults: list[SimpleOperationResult]):
        query = QSqlQuery(self.db)
        query.exec("begin exclusive transaction;")

        #self.db.transaction()

        query.prepare(
            "INSERT INTO Simple_Operation_Result(Operation_Id, Year, Month, Day, Hour, Success) VALUES (?,?,?,?,?,?)")

        for resultValue in SimpleOperationResults:
            query.addBindValue(resultValue.operationId)
            query.addBindValue(resultValue.year)
            query.addBindValue(resultValue.month)
            query.addBindValue(resultValue.day)
            query.addBindValue(resultValue.hour)
            query.addBindValue(resultValue.success)
            query.exec()

        #if not query.execBatch():
        #    x = query.lastError().text()
        #    logger.error(f"Insert Error (CampaignResultValue): {query.lastError().text()}")
        #    self.db.rollback()  # Rollback transaction on error
        #    return False
        query.exec("commit;")

        #self.db.commit()  # Commit the transaction
        return True

    def getTotalUnoperableSlotsPerMonth(self):
        allResults = self.getAllRows()
        allResults = [x for x in allResults if not x.success]

        totalUnoperableSlotsPerMonth: dict[str, list[list[QDateTime, float]]] = dict()

        for result in allResults:
            operation_id = result.operationName
            year = result.year
            month = result.month
            date = QDateTime()
            date.setDate(QDate(year, month, 15))

            # Check if the operation_id already exists in the dictionary
            if operation_id in totalUnoperableSlotsPerMonth:
                # Check if the date is the same as the last entry's date
                last_entry = totalUnoperableSlotsPerMonth[operation_id][-1]
                if last_entry[0] == date:
                    last_entry[1] += 1*3  # Increment the count
                else:
                    totalUnoperableSlotsPerMonth[operation_id].append([date, 1*3])  # New date entry
            else:
                # If operation_id doesn't exist, create a new entry
                totalUnoperableSlotsPerMonth[operation_id] = [[date, 1*3]]

        return totalUnoperableSlotsPerMonth
