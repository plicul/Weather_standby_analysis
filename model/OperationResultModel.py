import math
from datetime import timedelta, datetime
from typing import Optional

from PySide6.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
import logging

from consts.types import SeaData, OperationResult, Operation, LimitValue, SeaDataDate, CampaignOperation

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
    if relativeDir < 0:
        relativeDir += 360
    return relativeDir


def limitCheck(waveHeight: float, waveDir: float, wavePeriod: float, shipDir: float, limitVals: list[LimitValue]):
    relativeDir = getRelativeDir(waveDir, shipDir)
    waveHeightLimit = findWaveHeightLimit(limitVals=limitVals, relativeDir=relativeDir, wavePeriod=wavePeriod)
    if waveHeightLimit < waveHeight or waveHeightLimit == -1:
        return False
    return True


def successCheck(shipDir: float, limitVals: list[LimitValue], seaDataList: list[SeaData], operationType: str):
    for seaData in seaDataList:
        if not limitCheck(seaData.waveHeight, seaData.waveDir, seaData.wavePeriod, shipDir, limitVals):
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
            timeSlotsReq = math.ceil(operation.timeReq // 3)
            seaDataIndex = seaDataList.index(seaData)
            seaDataTimeSlots: list[SeaData] = []
            for timeSlot in range(timeSlotsReq):
                seaDataTimeSlots.append(seaDataList[seaDataIndex + timeSlot])

            operationResult = OperationResult(
                operationId=operation.id,
                year=seaData.year,
                month=seaData.month,
                day=seaData.day,
                hour=seaData.hour,
                success=successCheck(operation.shipDir, operation.limit.values, seaDataTimeSlots, operation.type)
            )
            self.insertRowData(operationResult)
        return

    def getFirstPassingDate(self, currentDate: SeaDataDate, operation: CampaignOperation):
        query = QSqlQuery()
        query.prepare("""
                SELECT opRes.Year, opRes.Month, opRes.Day, opRes.Hour, opRes.Success, op.Time_Req
                FROM Operation_Result as opRes left join operation op on opRes.operation_Id = op.Id 
                WHERE opRes.operation_Id = :operationId
                  AND (opRes.Year > :year 
                       OR (opRes.Year = :year AND opRes.Month > :month)
                       OR (opRes.Year = :year AND opRes.Month = :month AND opRes.Day > :day)
                       OR (opRes.Year = :year AND opRes.Month = :month AND opRes.Day = :day AND opRes.Hour >= :hour))
                  AND opRes.Success = 1
                ORDER BY Year, Month, Day, Hour
                LIMIT 1
            """)
        query.bindValue(":operationId", operation.operationId)
        query.bindValue(":year", currentDate.year)
        query.bindValue(":month", currentDate.month)
        query.bindValue(":day", currentDate.day)
        query.bindValue(":hour", currentDate.hour)

        if query.exec():
            if query.next():
                year = query.value(0)
                month = query.value(1)
                day = query.value(2)
                hour = query.value(3)
                first_passing_date = datetime(year, month, day, hour)

                end_date = first_passing_date + timedelta(hours=query.value(5) * 3)

                return SeaDataDate(first_passing_date.year, first_passing_date.month, first_passing_date.day, first_passing_date.hour), SeaDataDate(end_date.year, end_date.month, end_date.day, end_date.hour)
            else:
                logger.error("No passing date found that meets the criteria.")
                return None, None
        else:
            logger.error(f"Query Error: {query.lastError().text()}")
            return None, None
