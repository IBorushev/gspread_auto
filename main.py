import fire
import sys

import gspread
from isoweek import Week
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

from config import CityDict, Credentials
from load_data import FraudDetalizationTable, TotalFraudTable

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    Credentials.credentials, scope)

gc = gspread.authorize(credentials)


class Update():
    def Manual(self):

        while 1:
            print('Какой город будем обновлять?')
            for i in CityDict.city_dict.items():
                print('Код:' + i[0], i[1][0])
            city = input('\n' + 'Введите код города: ')
            if city in CityDict.city_dict.keys():
                break
            else:
                print('Города нет в справочнике. Попробуйте еще раз' + '\n')

        user_input = input('Через пробел укажите номер недели и год: ').split()
        if len(user_input) == 2:
            week, year = user_input[0], user_input[1]
        else:
            week, year = '1', '2019'
            print('Выбраны значения по умолчанию. Период: прошлая неделя')


        week, year, city, date_from, date_to, name_sheet, \
            min_trips_for_bonus = [i for i in prepareData(city, week, year)]

        wks = connect(city)

        createTable(wks, name_sheet)

        total_fraud_table, fraud_detalization_table = \
            [i for i in loadData(date_from, date_to, city, week, year, min_trips_for_bonus)]

        updateGspread(name_sheet, total_fraud_table, fraud_detalization_table, wks)

    def Auto(self, city, week='1', year='2019'):
        week, year, city, date_from, date_to, name_sheet, \
            min_trips_for_bonus = [i for i in prepareData(city, week, year)]

        wks = connect(city)

        createTable(wks, name_sheet)

        total_fraud_table, fraud_detalization_table = \
            [i for i in loadData(date_from, date_to, city, week, year, min_trips_for_bonus)]

        updateGspread(name_sheet, total_fraud_table, fraud_detalization_table, wks)


def connect(city):
    return gc.open_by_key(CityDict.city_gspread_key[city])


def prepareData(city, week=1, year=2019):
    if week == '1':
        week = datetime.today().isocalendar()[1] - 1

    if year == '2019':
        year = datetime.today().isocalendar()[0]

    city = str(city)

    date_from, date_to = Week(int(year), int(week)).monday().strftime('%Y%m%d'), \
        Week(int(year), int(week)).sunday().strftime('%Y%m%d')
    
    name_sheet = date_from[:4] + '.' + date_from[4:6] + '.' + date_from[6:] + ' - ' \
        + date_to[:4] + '.' + date_to[4:6] + '.' + date_to[6:]

    min_trips_for_bonus = CityDict.city_bonus_plan_dict[city][-1][0]
    return week, year, city, date_from, date_to, name_sheet, min_trips_for_bonus


def createTable(wks, name_sheet):
    check_worksheet_name = 0
    for i in wks.worksheets():
        if i.title != name_sheet:
            pass
        else:
            check_worksheet_name = 1

    if check_worksheet_name == 1:
        pass
    else:
        wks.duplicate_sheet(wks.worksheet('шаблон').id,
                            new_sheet_name=name_sheet)


def loadData(date_from, date_to, city, week, year, min_trips_for_bonus):
    total_fraud_table = TotalFraudTable(
        date_from, date_to, city, week, year, min_trips_for_bonus).values.tolist()

    drv_ids = [0, 0]
    for i in total_fraud_table:
        if i[8] != 0:
            drv_ids.append(i[1])
    drv_ids = tuple(drv_ids)

    fraud_detalization_table = FraudDetalizationTable(
        date_from, date_to, city, drv_ids).values.tolist()
    return total_fraud_table, fraud_detalization_table


def updateGspread(name_sheet, total_fraud_table, fraud_detalization_table, wks):
    wks.values_update(
        name_sheet + '!A4',
        params={
            'valueInputOption': 'USER_ENTERED'
        },
        body={
            'values': total_fraud_table
        }
    )

    wks.values_update(
        name_sheet + '!K4',
        params={
            'valueInputOption': 'USER_ENTERED'
        },
        body={
            'values': fraud_detalization_table
        }
    )


if __name__ == '__main__':
    fire.Fire(Update)