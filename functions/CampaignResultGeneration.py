from datetime import timedelta, datetime

from consts.types import Campaign, SeaDataDate, CampaignResult, CampaignResultValue, CampaignOperation
from model.CampaignModel import CampaignModel
from model.CampaignResultModel import CampaignResultModel
from model.OperationResultModel import OperationResultModel
from collections import deque


def generateCampaignResultValuesUntilFromTo(currentDate, firstPassingDate, endDate, operationId):
    result_values = []
    temp_date = currentDate
    while temp_date < firstPassingDate:
        result_values.append(
            CampaignResultValue(None, temp_date.year, temp_date.month, temp_date.day, temp_date.hour, operationId,
                                'wait'))
        temp_date += timedelta(hours=3)

    result_values.append(CampaignResultValue(None, firstPassingDate.year, firstPassingDate.month, firstPassingDate.day,
                                             firstPassingDate.hour, operationId, 'start'))

    temp_date = firstPassingDate + timedelta(hours=3)
    while temp_date < endDate:
        result_values.append(
            CampaignResultValue(None, temp_date.year, temp_date.month, temp_date.day, temp_date.hour, operationId,
                                'work'))
        temp_date += timedelta(hours=3)

    result_values.append(
        CampaignResultValue(None, endDate.year, endDate.month, endDate.day, endDate.hour, operationId, 'finish'))

    return result_values


def checkNextOperation(nextOperation, firstPassingDate, endDate, operationResultModel):
    """
    if nextOperation.relation == "F-S_NF":
        nextOpFirstPassingDate, endDateNew = operationResultModel.getFirstPassingDate(endDate, nextOperation)
        return endDate <= nextOpFirstPassingDate
    elif nextOperation.relation == "F-S_F":
        nextOpFirstPassingDate, endDateNew = operationResultModel.getFirstPassingDate(endDate, nextOperation)
        return endDate == nextOpFirstPassingDate
    elif nextOperation.relation == "S-S_NF":
        nextOpFirstPassingDate, endDateNew = operationResultModel.getFirstPassingDate(firstPassingDate, nextOperation)
        return firstPassingDate <= nextOpFirstPassingDate
    elif nextOperation.relation == "S-S_F":
        nextOpFirstPassingDate, endDateNew = operationResultModel.getFirstPassingDate(firstPassingDate, nextOperation)
        return firstPassingDate == nextOpFirstPassingDate
    return False
    """
    nextOpFirstPassingDate, _ = operationResultModel.getFirstPassingDate(endDate,
                                                                         nextOperation) if nextOperation.relation in [
        "F-S_NF", "F-S_F"] else operationResultModel.getFirstPassingDate(firstPassingDate, nextOperation)
    return endDate <= nextOpFirstPassingDate if nextOperation.relation in ["F-S_NF",
                                                                           "F-S_F"] else firstPassingDate <= nextOpFirstPassingDate


def getLastEndDate(cmpResultVals):
    end_dates = [val for val in cmpResultVals if val.status == 'finish']
    #if end_dates:
    #    last_end_date = end_dates[-1]
    #    return SeaDataDate(last_end_date.year, last_end_date.month, last_end_date.day, last_end_date.hour)
    #return None
    return SeaDataDate(end_dates[-1].year, end_dates[-1].month, end_dates[-1].day,
                       end_dates[-1].hour) if end_dates else None


def getLastStartDate(cmpResultVals):
    start_dates = [val for val in cmpResultVals if val.status == 'start']
    #if start_dates:
    #    last_start_date = start_dates[-1]
    #    return SeaDataDate(last_start_date.year, last_start_date.month, last_start_date.day, last_start_date.hour)
    #return None
    return SeaDataDate(start_dates[-1].year, start_dates[-1].month, start_dates[-1].day,
                       start_dates[-1].hour) if start_dates else None


def nextDate(date):
    #dt = datetime(date.year, date.month, date.day, date.hour)
    #next_dt = dt + timedelta(hours=3)
    #return SeaDataDate(next_dt.year, next_dt.month, next_dt.day, next_dt.hour)
    next_dt = datetime(date.year, date.month, date.day, date.hour) + timedelta(hours=3)
    return SeaDataDate(next_dt.year, next_dt.month, next_dt.day, next_dt.hour)


def getTotalWait(cmpResultVals):
    return sum(1 for val in cmpResultVals if val.status == 'wait')


def getTotalWork(cmpResultVals):
    return sum(1 for val in cmpResultVals if val.status == 'work' or val.status == 'finish' or val.status == 'start')


def generateCampaignResultValues(campaignId, operations, date: SeaDataDate,
                                 operationResultModel: OperationResultModel) -> CampaignResult:
    #TODO probaj izvrsit campaign u najmanje vremena postivajuc pravila meduzavisnosti

    operationsStack: list[CampaignOperation] = operations.copy()
    processedOperations: list[CampaignOperation] = []

    cmpResultVals: list[CampaignResultValue] = []
    currentDate = date
    originalDate = date

    operation = None
    nextOperation = None
    while operationsStack:
        operation = operationsStack.pop()
        #if len(operationsStack) > 0:
        #    nextOperation = operationsStack.pop()
        #    operationsStack.append(nextOperation)
        nextOperation = operationsStack[-1] if operationsStack else None
        processedOperations.append(operation)

        firstPassingDate, endDate = operationResultModel.getFirstPassingDate(currentDate, operation)

        # kreiraj listu za CampaignResultValue instance za sve datume do first passing date, stavi ih u wait
        # first passing date stavi u start
        # sve do end date stavi u work
        # end date u finish
        cmpResultValsTemp: list[CampaignResultValue] = generateCampaignResultValuesUntilFromTo(currentDate,
                                                                                               firstPassingDate,
                                                                                               endDate,
                                                                                               operation.operationId)
        # if checkNextOp saljemo sljedeci operation, tamo se onda provjerava ovisno o sljedu
        # ako je rel = mora poceti kada zavrsi -> je li start date te operacije = end date trenutne op
        # ako je rel = mora poceti istovremeno -> je li start date te op = start date trenutne op
        # ako je rel = moze poceti istovremeno -> trazimo start date koji je >= trenutnom dateu
        # U SVAKOM SLUCAJU AKO NE USPIJEMO NACI -> KRECEMO ISPOCETKA BRISEMO SVE SAMO POMICEMO START DATE
        # inace nastavi
        # save liste na nacin da se doda u cmpResultVals
        if not nextOperation  or checkNextOperation(nextOperation, firstPassingDate, endDate, operationResultModel):
            cmpResultVals.extend(cmpResultValsTemp)
            # ovisno o tipu relationship sljedeceg current date je ili start ili end date
            if nextOperation is None:
                continue
            if nextOperation.relation == "F-S_NF" or nextOperation.relation == "F-S_F":
                currentDate = endDate
            else:
                currentDate = firstPassingDate
        else:
            while processedOperations and not (processedOperations[-1].relation in ["F-S_NF", "S-S_NF"]):
                lastPop = processedOperations.pop()
                cmpResultVals = [val for val in cmpResultVals if val.operation_id != lastPop.operationId]
                operationsStack.append(lastPop)

            if cmpResultVals:
                lastOp = processedOperations[-1] if processedOperations else None
                if lastOp and lastOp.relation in ["F-S_NF", "F-S_F"]:
                    currentDate = nextDate(getLastEndDate(cmpResultVals))
                else:
                    currentDate = nextDate(getLastStartDate(cmpResultVals))
            else:
                currentDate = nextDate(originalDate)
                originalDate = currentDate
        """
        else:
            # operationsStack = generateOperationsQueue(operations)
            lastPop = processedOperations.pop()
            while lastPop.relation != "F-S_NF" or lastPop.relation != "S-S_NF":
                operationsStack.append(lastPop)
                cmpResultVals = filter(lambda cmpResultVal: cmpResultVal.operation_id != lastPop.operationId,
                                       cmpResultVals)
                lastPop = processedOperations.pop()

            # current date onda postaje ovisno o relationshipu novog sljedeceg po redu start ili end date prvog zadnjeg
            # ili originalni date
            if len(cmpResultVals) > 0:
                #nova sljedeca operacija
                if operationsStack[-1].relation == "F-S_NF" or operationsStack[-1].relation == "F-S_F":
                    currentDate = nextDate(getLastEndDate(cmpResultVals))
                else:
                    currentDate = nextDate(getLastStartDate(cmpResultVals))
            else:
                currentDate = nextDate(date)

            operation = None
            nextOperation = None
        """

        return CampaignResult(id=None, campaign_id=campaignId, year=date.year, month=date.month, day=date.day,
                              hour=date.hour, resultValues=cmpResultVals, success=True,
                              total_wait=getTotalWait(cmpResultVals), total_work=getTotalWork(cmpResultVals))


def simulateCampaign(campaign: Campaign, dates: list[SeaDataDate], campaignResultModel: CampaignResultModel,
                     operationResultModel: OperationResultModel) -> bool:
    try:
        a = 0
        for date in dates:
            a += 1
            cmpRes: CampaignResult = generateCampaignResultValues(campaign.id, campaign.operations, date,
                                                                  operationResultModel)
            campaignResultModel.insertCampaignResult(cmpRes)
        return True
    except Exception as e:
        return False
