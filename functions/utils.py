from datetime import datetime

import pandas as pd

from consts.types import LimitValue, Limit, SeaDataDate
from model.LimitModel import LimitModel


def seaDataToExcel():
    input_file = 'data.txt'
    output_file = '../data.csv'

    columns = ["YYYY", "MM", "DD", "HH", "mn", "Hs(m)", "Tp(s)", "TheH(°N)", "WS(m/s)", "Thew(°N)"]

    data = pd.read_csv(input_file, delim_whitespace=True, names=columns, skiprows=1, encoding='ISO-8859-1')

    data.to_csv(output_file, index=False)


def importLimitFromExcel(limitModel: LimitModel):
    input_file = './resources/Limit.xlsx'
    df = pd.read_excel(input_file, header=None)
    arr = df.values.tolist()

    limitVals = []
    waveDirs = arr[0][1:]
    for i in range(1, len(arr)):
        wave_period = arr[i][0]
        for j in range(1, len(arr[i])):
            wave_height = arr[i][j]
            wave_direction = waveDirs[j - 1]
            limitVal = LimitValue(wavePeriod=wave_period, waveDir=wave_direction, waveHeight=wave_height)
            limitVals.append(limitVal)
    newLimit: Limit = Limit(-1, limitVals)
    limitModel.insertLimit(newLimit)


def calcSeaDataDif(date1: SeaDataDate, date2: SeaDataDate):
    dt1 = datetime(date1.year, date1.month, date1.day, date1.hour)
    dt2 = datetime(date2.year, date2.month, date2.day, date2.hour)

    dif = dt2 - dt1

    hours_diff = dif.total_seconds() / 3600

    return hours_diff/3
