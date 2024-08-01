from PySide6.QtCore import QMetaType
from PySide6.QtSql import QSqlDatabase, QSqlQuery
import logging
from typing import List

from consts.types import CampaignResult, Operation, CampaignResultValue
from model.OperationModel import OperationModel

logger = logging.getLogger("logger")


class CampaignResultModel:
    def __init__(self, db=QSqlDatabase()):
        self.db = db

    def getCampaignResultsForCampaign(self, campaignId) -> list[CampaignResult] | None:
        query = QSqlQuery(self.db)
        query.prepare(
            "Select id, campaign_id, year, month, day, hour, total_wait, total_work, success from Campaign_Result as cmpRes where cmpRes.campaign_id = :campaignId")
        query.bindValue(":campaignId", campaignId)

        if not query.exec():
            logger.error(f"Query Error: {query.lastError().text()}")
            return None

        cmpResults: list[CampaignResult] = []

        while query.next():
            cmpResult = CampaignResult(
                id=query.value(0),
                campaign_id=query.value(1),
                year=query.value(2),
                month=query.value(3),
                day=query.value(4),
                hour=query.value(5),
                total_wait=query.value(6),
                total_work=query.value(7),
                success=query.value(8),
                resultValues=None
            )
            cmpResults.append(cmpResult)

        return cmpResults

    def getCampaignResultValuesForCampaignResult(self, campaignResultId) -> list[CampaignResultValue] | None:
        query = QSqlQuery(self.db)
        query.prepare(
            "Select cmpResVal.campaign_result_id, cmpResVal.year, cmpResVal.month, cmpResVal.day, cmpResVal.hour, cmpResVal.operation_id, cmpResVal.status, cmpResVal.campaign_operation_id, cmpOp.Relationship  from Campaign_Result_Value as cmpResVal left join main.Campaign_Operations cmpOp on cmpOp.id = cmpResVal.campaign_operation_id where cmpResVal.campaign_result_id = :campaignResultId")
        query.bindValue(":campaignResultId", campaignResultId)

        if not query.exec():
            logger.error(f"Query Error: {query.lastError().text()}")
            return None

        cmpResultVals: list[CampaignResultValue] = []

        while query.next():
            cmpResultVal = CampaignResultValue(
                campaignResultId=query.value(0),
                year=query.value(1),
                month=query.value(2),
                day=query.value(3),
                hour=query.value(4),
                operationId=query.value(5),
                status=query.value(6),
                campaignOperationId=query.value(7),
                relationship=query.value(8),
            )
            cmpResultVals.append(cmpResultVal)

        return cmpResultVals

    def insertCampaignResultValuesBatch2(self, cmpResultValues: List[tuple[int, [CampaignResultValue]]]):
        query = QSqlQuery(self.db)
        query.exec("begin exclusive transaction;")

        #self.db.transaction()

        query.prepare(
            "INSERT INTO Campaign_Result_Value(campaign_result_id, year, month, day, hour, operation_id, status,campaign_operation_id) VALUES (?,?,?,?,?,?,?,?)")

        for resultValueTuple in cmpResultValues:
            for resultValue in resultValueTuple[1]:
                query.addBindValue(resultValueTuple[0])
                query.addBindValue(resultValue.year)
                query.addBindValue(resultValue.month)
                query.addBindValue(resultValue.day)
                query.addBindValue(resultValue.hour)
                query.addBindValue(resultValue.operationId)
                query.addBindValue(resultValue.status)
                query.addBindValue(resultValue.campaignOperationId)
                query.exec()

        #if not query.execBatch():
        #    x = query.lastError().text()
        #    logger.error(f"Insert Error (CampaignResultValue): {query.lastError().text()}")
        #    self.db.rollback()  # Rollback transaction on error
        #    return False
        query.exec("commit;")

        #self.db.commit()  # Commit the transaction
        return True

    def insertCampaignResultValuesBatch(self, cmpResultValues: List[tuple[int, [CampaignResultValue]]]):
        query = QSqlQuery(self.db)

        #self.db.transaction()
        query.exec("begin exclusive transaction;")

        query.prepare(
            "INSERT INTO Campaign_Result_Value(campaign_result_id, year, month, day, hour, operation_id, status,campaign_operation_id) VALUES (?,?,?,?,?,?,?,?)")

        campaignIds = []
        years = []
        months = []
        days = []
        hours = []
        operations = []
        statuses = []
        campaignOperations = []

        for resultValueTuple in cmpResultValues:
            for resultValue in resultValueTuple[1]:
                campaignIds.append(resultValueTuple[0])
                years.append(resultValue.year)
                months.append(resultValue.month)
                days.append(resultValue.day)
                hours.append(resultValue.hour)
                operations.append(resultValue.operationId)
                statuses.append(resultValue.status)
                campaignOperations.append(resultValue.campaignOperationId)

        query.addBindValue(campaignIds)
        query.addBindValue(years)
        query.addBindValue(months)
        query.addBindValue(days)
        query.addBindValue(hours)
        query.addBindValue(operations)
        query.addBindValue(statuses)
        query.addBindValue(campaignOperations)

        if not query.execBatch():
            x = query.lastError().text()
            logger.error(f"Insert Error (CampaignResultValue): {query.lastError().text()}")
            #self.db.rollback()  # Rollback transaction on error
            return False
        query.exec("commit;")
        #self.db.commit()  # Commit the transaction
        return True

    def insertCampaignResultValues(self, campaignResultId, resultValues: List[CampaignResultValue]):
        query = QSqlQuery(self.db)

        self.db.transaction()

        query.prepare(
            "INSERT INTO Campaign_Result_Value(campaign_result_id, year, month, day, hour, operation_id, status,campaign_operation_id) VALUES (?,?,?,?,?,?,?,?)")

        campaignIds = []
        years = []
        months = []
        days = []
        hours = []
        operations = []
        statuses = []
        campaignOperations = []

        for resultValue in resultValues:
            campaignIds.append(campaignResultId)
            years.append(resultValue.year)
            months.append(resultValue.month)
            days.append(resultValue.day)
            hours.append(resultValue.hour)
            operations.append(resultValue.operationId)
            statuses.append(resultValue.status)
            campaignOperations.append(resultValue.campaignOperationId)

        query.addBindValue(campaignIds)
        query.addBindValue(years)
        query.addBindValue(months)
        query.addBindValue(days)
        query.addBindValue(hours)
        query.addBindValue(operations)
        query.addBindValue(statuses)
        query.addBindValue(campaignOperations)

        if not query.execBatch():
            x = query.lastError().text()
            logger.error(f"Insert Error (CampaignResultValue): {query.lastError().text()}")
            self.db.rollback()  # Rollback transaction on error
            return False

        self.db.commit()  # Commit the transaction
        return True
        """
        for resultValue in resultValues:
            query.prepare(
                "INSERT INTO Campaign_Result_Value(campaign_result_id, year, month, day, hour, operation_id, status,campaign_operation_id) VALUES (?,?,?,?,?,?,?,?)")
            query.addBindValue(campaignResultId)
            query.addBindValue(resultValue.year)
            query.addBindValue(resultValue.month)
            query.addBindValue(resultValue.day)
            query.addBindValue(resultValue.hour)
            query.addBindValue(resultValue.operationId)
            query.addBindValue(resultValue.status)
            query.addBindValue(resultValue.campaignOperationId)

            if not query.exec():
                x = query.lastError().text()
                logger.error(f"Insert Error (CampaignResultValue): {query.lastError().text()}")
                self.db.rollback()  # Rollback transaction on error
                return False

            query.clear()  # Clear the query to reuse it

        self.db.commit()  # Commit the transaction
        return True
"""

    # We always get a full Campaign Result object here
    def insertCampaignResults(self, campaignResults: list[CampaignResult]) -> bool:
        query = QSqlQuery(self.db)
        query.exec("begin exclusive transaction;")
        #self.db.transaction()

        cmpResultValues: List[tuple[int, [CampaignResultValue]]] = []
        for campaignResult in campaignResults:
            query.prepare(
                "INSERT INTO Campaign_Result(campaign_id, year, month, day, hour, total_wait, total_work, success) VALUES (?,?,?,?,?,?,?,?)")
            query.addBindValue(campaignResult.campaign_id)
            query.addBindValue(campaignResult.year)
            query.addBindValue(campaignResult.month)
            query.addBindValue(campaignResult.day)
            query.addBindValue(campaignResult.hour)
            query.addBindValue(campaignResult.total_wait)
            query.addBindValue(campaignResult.total_work)
            query.addBindValue(1 if campaignResult.success else 0)
            if not query.exec():
                logger.error(f"Insert Error (CampaignResult): {query.lastError().text()}")
                return False
            query.clear()
            query.prepare("Select max(id) from Campaign_Result")
            query.exec()
            query.next()
            campaignResultId = query.value(0)
            cmpResultValTuple: tuple[int, CampaignResultValue] = tuple((campaignResultId, campaignResult.resultValues))
            cmpResultValues.append(cmpResultValTuple)
            #try:
            #    if not self.insertCampaignResultValues(campaignResultId, campaignResult.resultValues):
            #        return False
            #except Exception as e:
            #    b = e
        query.exec("commit;")
        try:
            if not self.insertCampaignResultValuesBatch2(cmpResultValues):
                return False
        except Exception as e:
            b = e
        #self.db.commit()

        return True

    def getAllCampaignResults(self):
        query = QSqlQuery(self.db)
        query.prepare(
            "Select cmpRes.id, cmpRes.campaign_id, cmpRes.year, cmpRes.month, cmpRes.day, cmpRes.hour from Campaign_Result as cmpRes")  # left join main.Campaign C on C.Id = cmpRes.campaign_id")
        query.exec()
        cmpResList: list[CampaignResult] = []
        while query.next():
            cmpResList.append(CampaignResult(id=query.value(0), campaign_id=query.value(1), resultValues=None,
                                             year=query.value(2), month=query.value(3), day=query.value(4),
                                             hour=query.value(5),
                                             total_wait=None, total_work=None, success=None))
        return cmpResList

    # TODO
    def getTotalWaitTotalWork(self, campaignId):
        query = QSqlQuery(self.db)

        totalWait = 0
        totalWork = 0

        query.prepare(
            "Select count(*) from Campaign_Result_Value as cmpResVal left join main.Campaign_Operations cmpOp on cmpOp.id = cmpResVal.campaign_operation_id where cmpOp.campaign_id = :campaignId and cmpResVal.status = 'wait'")
        query.bindValue(":campaignId", campaignId)

        if not query.exec():
            logger.error(f"Query Error: {query.lastError().text()}")
            return None, None
        query.next()
        totalWait = query.value(0)

        query.clear()
        query.prepare(
            "Select count(*) from Campaign_Result_Value as cmpResVal left join main.Campaign_Operations cmpOp on cmpOp.id = cmpResVal.campaign_operation_id where cmpOp.campaign_id = :campaignId and cmpResVal.status != 'wait'")
        query.bindValue(":campaignId", campaignId)

        if not query.exec():
            logger.error(f"Query Error: {query.lastError().text()}")
            return None, None
        query.next()
        totalWork = query.value(0)

        return totalWait, totalWork

    def calcTotalWaitTimePerYear(self, selectedCampaignId) -> list[tuple[str, int]]:
        data: list[CampaignResult] = self.getCampaignResultsForCampaign(selectedCampaignId)

        waitTimePerYear: list[tuple[str, int]] = []
        year = data[0].year
        cmpsInyear = list(filter(lambda dataVal: dataVal.year == year, data))
        waitTimePerYearTuple: tuple[str, int] = year.__str__(), sum(
            map(lambda cmpInYear: cmpInYear.total_wait, cmpsInyear))
        while waitTimePerYearTuple[1] != 0:
            waitTimePerYear.append(waitTimePerYearTuple)
            year += 1
            cmpsInyear = list(filter(lambda dataVal: dataVal.year == year, data))
            waitTimePerYearTuple: tuple[str, int] = year.__str__(), sum(
                map(lambda cmpInYear: cmpInYear.total_wait, cmpsInyear))
        return waitTimePerYear

    def calcAvgWaitTimePerYear(self, selectedCampaignId) -> list[tuple[str, float]]:
        data: list[CampaignResult] = self.getCampaignResultsForCampaign(selectedCampaignId)

        waitTimePerYear: list[tuple[str, float]] = []
        if(len(data) == 0):
            return waitTimePerYear
        year = data[0].year
        cmpsInYear = list(filter(lambda dataVal: dataVal.year == year, data))
        waitTimePerYearTuple: tuple[str, float] = year.__str__(), sum(
            map(lambda cmpInYear: cmpInYear.total_wait, cmpsInYear)) / len(cmpsInYear)
        while waitTimePerYearTuple[1] != 0:
            waitTimePerYear.append(waitTimePerYearTuple)
            year += 1
            cmpsInYear = list(filter(lambda dataVal: dataVal.year == year, data))
            if len(cmpsInYear) == 0:
                waitTimePerYearTuple = year.__str__(), 0
                continue
            waitTimePerYearTuple: tuple[str, float] = year.__str__(), sum(
                map(lambda cmpInYear: cmpInYear.total_wait, cmpsInYear)) / len(cmpsInYear)
        return waitTimePerYear

    def calcTotalWaitTimePerMonth(self, selectedCampaignId, year) -> list[tuple[str, float]]:
        data: list[CampaignResult] = self.getCampaignResultsForCampaign(selectedCampaignId)

        waitTimePerMonth: list[tuple[str, float]] = []
        month = 1
        cmpsInMonth = list(filter(lambda dataVal: dataVal.year == year and dataVal.month == month, data))
        waitTimePerMonthTuple: tuple[str, float] = month.__str__(), sum(
            map(lambda cmpInYear: cmpInYear.total_wait, cmpsInMonth))
        while month < 13:
            waitTimePerMonth.append(waitTimePerMonthTuple)
            month += 1
            cmpsInMonth = list(filter(lambda dataVal: dataVal.year == year and dataVal.month == month, data))
            if len(cmpsInMonth) == 0:
                waitTimePerMonthTuple = month.__str__(), 0
                continue
            waitTimePerMonthTuple: tuple[str, float] = month.__str__(), sum(
                map(lambda cmpInYear: cmpInYear.total_wait, cmpsInMonth))
        return waitTimePerMonth

    def calcAvgWaitTimePerMonth(self, selectedCampaignId, year) -> list[tuple[str, float]]:
        data: list[CampaignResult] = self.getCampaignResultsForCampaign(selectedCampaignId)

        waitTimePerMonth: list[tuple[str, float]] = []
        month = 1
        cmpsInMonth = list(filter(lambda dataVal: dataVal.year == year and dataVal.month == month, data))
        waitTimePerMonthTuple: tuple[str, float] | None = None
        if len(cmpsInMonth) == 0:
            waitTimePerMonthTuple = month.__str__(), 0
        else:
            waitTimePerMonthTuple = month.__str__(), sum(
                map(lambda cmpInYear: cmpInYear.total_wait, cmpsInMonth)) / len(cmpsInMonth)
        while month < 13:
            waitTimePerMonth.append(waitTimePerMonthTuple)
            month += 1
            cmpsInMonth = list(filter(lambda dataVal: dataVal.year == year and dataVal.month == month, data))
            if len(cmpsInMonth) == 0:
                waitTimePerMonthTuple = month.__str__(), 0
                continue
            waitTimePerMonthTuple: tuple[str, float] = month.__str__(), sum(
                map(lambda cmpInYear: cmpInYear.total_wait, cmpsInMonth)) / len(cmpsInMonth)
        return waitTimePerMonth
