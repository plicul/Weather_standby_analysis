import bisect
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
    return relativeDir
    #if relativeDir < 0:
    #    relativeDir += 360


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
        self.db = db
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

    def getAllRows(self) -> dict[int, list[OperationResult]]:
        operation_dict = {}
        query = QSqlQuery(self.db)
        query.prepare("SELECT Operation_Id, Year, Month, Day, Hour, Success FROM Operation_Result WHERE Success = 1")

        if not query.exec():
            logger.error(f"Query Error: {query.lastError().text()}")
            return {}

        while query.next():
            operationId = query.value("Operation_Id")
            operationRes = OperationResult(
                operationId=operationId,
                year=query.value("Year"),
                month=query.value("Month"),
                day=query.value("Day"),
                hour=query.value("Hour"),
                success=query.value("Success")
            )

            # Add the operation result to the dictionary
            if operationId not in operation_dict:
                operation_dict[operationId] = []
            operation_dict[operationId].append(operationRes)

        return operation_dict

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
        operationResults = []
        for seaData in seaDataList:
            timeSlotsReq = math.ceil(operation.timeReq // 3)
            seaDataIndex = seaDataList.index(seaData)
            seaDataTimeSlots: list[SeaData] = []
            if seaDataIndex + timeSlotsReq >= len(seaDataList):
                operationResult = OperationResult(
                    operationId=operation.id,
                    year=seaData.year,
                    month=seaData.month,
                    day=seaData.day,
                    hour=seaData.hour,
                    success=False
                )
                continue
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
            operationResults.append(operationResult)
            #self.insertRowData(operationResult)
        self.insertRowDataQuery(operationResults)
        return
    """
    def getFirstPassingDate(self, currentDate: SeaDataDate, operation: CampaignOperation,
                            operationsResults: list[OperationResult], operationLenMap: dict[int, int]):
        def is_valid(res):
            # Returns True if the result meets the criteria
            return (res.operationId == operation.operationId and
                    res.success == 1 and
                    (res.year > currentDate.year or
                     (res.year == currentDate.year and res.month > currentDate.month) or
                     (res.year == currentDate.year and res.month == currentDate.month and res.day > currentDate.day) or
                     (res.year == currentDate.year and res.month == currentDate.month and res.day == currentDate.day and res.hour >= currentDate.hour)))

        # Using bisect to find the starting index of the first valid result
        start_index = bisect.bisect_left(operationsResults, currentDate,
                                         key=lambda res: SeaDataDate(res.year, res.month, res.day, res.hour))

        # Iterating from the found index to check for the first valid result
        for i in range(start_index, len(operationsResults)):
            res = operationsResults[i]
            if is_valid(res):
                first_passing_date = datetime(res.year, res.month, res.day, res.hour)
                end_date = first_passing_date + timedelta(hours=operationLenMap[res.operationId] * 3)
                return SeaDataDate(first_passing_date.year, first_passing_date.month, first_passing_date.day, first_passing_date.hour), SeaDataDate(end_date.year, end_date.month, end_date.day, end_date.hour)

        # If no matching result is found
        logger.info("No passing date found that meets the criteria.")
        return None, None
    """
    def getFirstPassingDate(self, currentDate: SeaDataDate, operation: CampaignOperation,
                            operationsResults: list[OperationResult], operationLenMap: dict[int, int]):
        # Iterate through the sorted operationsResults
        for res in operationsResults:
            # Check if the operationId matches
            if res.operationId == operation.operationId:
                # Check if the result date is after the currentDate
                if (res.year > currentDate.year
                        or (res.year == currentDate.year and res.month > currentDate.month)
                        or (res.year == currentDate.year and res.month == currentDate.month and res.day > currentDate.day)
                        or (res.year == currentDate.year and res.month == currentDate.month and res.day == currentDate.day and res.hour >= currentDate.hour)):
                    # Check if the operation was successful
                    if res.success == 1:
                        # Found the first matching result
                        first_passing_date = datetime(res.year, res.month, res.day, res.hour)

                        # Calculate the end date using the operation length map
                        end_date = first_passing_date + timedelta(hours=operationLenMap[res.operationId] * 3)

                        return SeaDataDate(first_passing_date.year, first_passing_date.month, first_passing_date.day,
                                           first_passing_date.hour), SeaDataDate(end_date.year, end_date.month, end_date.day,
                                                                                 end_date.hour)
        # If no matching result is found
        logger.info("No passing date found that meets the criteria.")
        return None, None

    def insertRowDataQuery(self, operationResults: list[OperationResult]):
        query = QSqlQuery(self.db)
        query.exec("begin exclusive transaction;")

        #self.db.transaction()

        query.prepare(
            "INSERT INTO Operation_Result(Operation_Id, Year, Month, Day, Hour, Success) VALUES (?,?,?,?,?,?)")

        for resultValue in operationResults:
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
