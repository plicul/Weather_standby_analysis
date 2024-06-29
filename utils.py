import pandas as pd

from consts.types import LimitValue, Limit
from model.LimitModel import LimitModel


def seaDataToExcel():
    input_file = 'data.txt'
    output_file = 'data.csv'

    columns = ["YYYY", "MM", "DD", "HH", "mn", "Hs(m)", "Tp(s)", "TheH(°N)", "WS(m/s)", "Thew(°N)"]

    data = pd.read_csv(input_file, delim_whitespace=True, names=columns, skiprows=1, encoding='ISO-8859-1')

    data.to_csv(output_file, index=False)


def importLimitFromExcel(limitModel: LimitModel):
    input_file = 'resources\\limit.xlsx'
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

