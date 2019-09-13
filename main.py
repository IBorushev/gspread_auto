import gspread
from isoweek import Week
from oauth2client.service_account import ServiceAccountCredentials
from load_data import TotalFraudTable, FraudDetalizationTable
from config import Credentials, CityDict


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(Credentials.credentials, scope)

gc = gspread.authorize(credentials)

class ManualUpdate():
    # block 1
    print('Какой город будем обновлять?')
    for i in CityDict.city_dict.items():
        print('№:' + i[0], i[1][0], i[1][1])

    user_city_id = input('Введите номер города: ')



    city_id = CityDict.city_dict[user_city_id][1]

    week, year = input('Через пробел укажите номер недели и год: ').split()

    date_from, date_to = Week(int(year), int(week)).monday().strftime('%Y%m%d'), \
                                Week(int(year), int(week)).sunday().strftime('%Y%m%d')
    name_sheet = date_from[:4] + '.' + date_from[4:6] + '.' + date_from[6:] + ' - ' \
                                + date_to[:4] + '.' + date_to[4:6] + '.' + date_to[6:]
    # block 2
    wks = gc.open_by_key(CityDict.city_gspread_key[user_city_id])

    # Checking a sheet with the name *** already exists
    # If the sheet not exists then create the new sheet with name ***
    check_worksheet_name = 0
    for i in wks.worksheets():
        if i.title != name_sheet:
            pass
        else:
            check_worksheet_name = 1

    if check_worksheet_name == 1:
        pass
    else:
        wks.duplicate_sheet(wks.worksheet('шаблон').id, new_sheet_name= name_sheet)
    # End check

    total_fraud_table = TotalFraudTable(date_from, date_to, city_id, week, year).values.tolist()

    wks.values_update(
        name_sheet + '!A4',
        params={
            'valueInputOption': 'USER_ENTERED'
        },
        body={
            'values': total_fraud_table
        }
    )
    
    # block 3
    drv_ids = [0, 0]
    for i in total_fraud_table:
        if i[8] > 0:
            drv_ids.append(i[1])
    drv_ids = tuple(drv_ids)
    
    fraud_detalization_table = FraudDetalizationTable(date_from, date_to, city_id, drv_ids).values.tolist()

    wks.values_update(
        name_sheet + '!K4',
        params={
            'valueInputOption': 'USER_ENTERED'
        },
        body={
            'values': fraud_detalization_table
        }
    )
