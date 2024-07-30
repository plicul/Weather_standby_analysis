from PySide6.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
import logging

from consts.types import SeaData, SeaDataDate

logger = logging.getLogger("logger")


class SeaDataModel(QSqlTableModel):
    def __init__(self, parent=None, db=QSqlDatabase()):
        super(SeaDataModel, self).__init__(parent, db)
        self.db = db
        self.setTable("Sea_Data")
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)
        if not self.select():
            logger.error(f"Error: {self.lastError().text()}")
        else:
            logger.info("Model created and data selected successfully")

    def selectRow(self, row) -> SeaData:
        record = self.record(row)
        seaData = SeaData(
            year=record.value("Year"),
            month=record.value("Month"),
            day=record.value("Day"),
            hour=record.value("Hour"),
            waveHeight=record.value("Wave_Height"),
            waveDir=record.value("Wave_Dir"),
            wavePeriod=record.value("Wave_Period"),
        )
        return seaData

    def getAllRows(self) -> list[SeaData]:
        query = QSqlQuery(self.db)
        query.prepare("SELECT year, month, day, hour, wave_height, wave_dir, wave_period FROM Sea_Data")

        if not query.exec():
            logger.error(f"Query Error: {query.lastError().text()}")
            return []

        seaDataList = []
        while query.next():
            seaDataTmp = SeaData(year=query.value(0), month=query.value(1), day=query.value(2), hour=query.value(3),
                                 waveHeight=query.value(4),wavePeriod=query.value(5), waveDir=query.value(6))
            seaDataList.append(seaDataTmp)

        return seaDataList

        #rows = []
        #for row in range(self.rowCount()):
        #    rows.append(self.selectRow(row))
        #return rows

    def insertRowData(self, seaData: SeaData) -> bool:
        row = self.rowCount()
        self.insertRow(row)
        self.setData(self.index(row, self.fieldIndex("Year")), seaData.year)
        self.setData(self.index(row, self.fieldIndex("Month")), seaData.month)
        self.setData(self.index(row, self.fieldIndex("Day")), seaData.day)
        self.setData(self.index(row, self.fieldIndex("Hour")), seaData.hour)
        self.setData(self.index(row, self.fieldIndex("Wave_Height")), seaData.waveHeight)
        self.setData(self.index(row, self.fieldIndex("Wave_Dir")), seaData.waveDir)
        self.setData(self.index(row, self.fieldIndex("Wave_Period")), seaData.waveDir)
        if not self.submitAll():
            logger.error(f"Insert Error: {self.lastError().text()}")
            return False
        logger.info("Row inserted successfully")
        return True

    def getSeaDataDateRange(self) -> list[SeaDataDate]:
        query = QSqlQuery(self.db)
        query.prepare("SELECT year, month, day, hour FROM Sea_Data where Hour = 0 ")

        if not query.exec():
            logger.error(f"Query Error: {query.lastError().text()}")
            return []

        seaDataDateList = []
        while query.next():
            seaDataTmp = SeaDataDate(year=query.value(0), month=query.value(1), day=query.value(2), hour=query.value(3))
            seaDataDateList.append(seaDataTmp)

        return seaDataDateList
