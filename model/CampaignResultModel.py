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
                operation_id=query.value(5),
                status=query.value(6),
                campaignOperationId= query.value(7),
                relationship= query.value(8),
            )
            cmpResultVals.append(cmpResultVal)

        return cmpResultVals

    def insertCampaignResultValues(self, campaignResultId, resultValues: List[CampaignResultValue]):
        query = QSqlQuery(self.db)


        self.db.transaction()

        for resultValue in resultValues:
            query.prepare(
                "INSERT INTO Campaign_Result_Value(campaign_result_id, year, month, day, hour, operation_id, status,campaign_operation_id) VALUES (?,?,?,?,?,?,?,?)")
            query.addBindValue(campaignResultId)
            query.addBindValue(resultValue.year)
            query.addBindValue(resultValue.month)
            query.addBindValue(resultValue.day)
            query.addBindValue(resultValue.hour)
            query.addBindValue(resultValue.operation_id)
            query.addBindValue(resultValue.status)
            query.addBindValue(resultValue.campaignOperationId)

            if not query.exec():
                x= query.lastError().text()
                logger.error(f"Insert Error (CampaignResultValue): {query.lastError().text()}")
                self.db.rollback()  # Rollback transaction on error
                return False

            query.clear()  # Clear the query to reuse it

        self.db.commit()  # Commit the transaction
        return True

    # We always get a full Campaign Result object here
    def insertCampaignResult(self, campaignResult: CampaignResult) -> bool:
        query = QSqlQuery(self.db)
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

        #query.clear()
        query.prepare("Select max(id) from Campaign_Result")
        query.exec()
        query.next()
        campaignResultId = query.value(0)
        query.clear()

        if not self.insertCampaignResultValues(campaignResultId, campaignResult.resultValues):
            return False

        return True


'''
 def insertCampaignResultValue(self, campaignResultId, resultValue):
     query = QSqlQuery(self.db)
     query.prepare("INSERT INTO Campaign_Result_Value(campaign_result_id, year, month, day, hour, operation_id, status) VALUES (?,?,?,?,?,?,?)")
     query.addBindValue(campaignResultId)
     query.addBindValue(resultValue.year)
     query.addBindValue(resultValue.month)
     query.addBindValue(resultValue.day)
     query.addBindValue(resultValue.hour)
     query.addBindValue(resultValue.operation_id)
     query.addBindValue(resultValue.status)

     if not query.exec():
         a = query.lastError().text()
         logger.error(f"Insert Error (CampaignResultValue): {query.lastError().text()}")
         return False
 '''
