from PySide6.QtSql import QSqlDatabase, QSqlQuery
import logging
from typing import List

from consts.types import Campaign, CampaignOperation, Operation
from model.OperationModel import OperationModel

logger = logging.getLogger("logger")


class CampaignModel:
    def __init__(self, db=QSqlDatabase()):
        self.db = db

    def getCampaign(self, campaignId) -> Campaign | None:
        query = QSqlQuery(self.db)
        query.prepare("SELECT cmp.Id, cmp_op.Operation_Id, cmp_op.Relationship, cmp_op.[order], cmp_op.id FROM Campaign as cmp "
                      "left join Campaign_Operations as cmp_op on cmp.Id = cmp_op.Campaign_Id left join Operation as op on cmp_op.Operation_Id = op.Id where cmp.Id = :campaignId")
        query.bindValue(":campaignId", campaignId)

        if not query.exec():
            logger.error(f"Query Error: {query.lastError().text()}")
            return None

        cmpOperations: list[CampaignOperation] = []

        while query.next():
            cmpOperationTmp = CampaignOperation(
                operationId=query.value(1),
                order=query.value(3),
                relation=query.value(2),
                id=query.value(4)
            )
            cmpOperations.append(cmpOperationTmp)
        cmpOperations.sort(key=lambda cmpOperation: cmpOperation.order, reverse=True)
        return Campaign(
            id=campaignId,
            operations=cmpOperations
        )

    def getAllCampaigns(self, limitModel) -> List[Campaign | None]:
        query = QSqlQuery(self.db)
        query.prepare("SELECT Id FROM Campaign")

        if not query.exec():
            logger.error(f"Query Error: {query.lastError().text()}")
            return []

        campaigns = []
        while query.next():
            campaignId = query.value(0)
            campaign = self.getCampaign(campaignId, limitModel)
            if campaign:
                campaigns.append(campaign)

        return campaigns

    def getAllCampaignIds(self) -> List[Campaign | None]:
        query = QSqlQuery(self.db)
        query.prepare("SELECT Id FROM Campaign")

        if not query.exec():
            logger.error(f"Query Error: {query.lastError().text()}")
            return []

        campaigns = []
        while query.next():
            campaignId = query.value(0)
            campaigns.append(campaignId)

        return campaigns

    def insertCampaign(self, campaign: Campaign) -> bool:
        query = QSqlQuery(self.db)
        query.prepare("INSERT INTO Campaign DEFAULT VALUES")

        #TODO insert cmp operations

        if not query.exec():
            logger.error(f"Insert Error (Campaign): {query.lastError().text()}")
            return False

        return True
