import pandas as pd


def seaDataToExcel():
    input_file = 'data.txt'
    output_file = 'data.csv'

    columns = ["YYYY", "MM", "DD", "HH", "mn", "Hs(m)", "Tp(s)", "TheH(°N)", "WS(m/s)", "Thew(°N)"]

    data = pd.read_csv(input_file, delim_whitespace=True, names=columns, skiprows=1, encoding='ISO-8859-1')

    data.to_csv(output_file, index=False)
