import os

from dotenv import load_dotenv
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class ConnectToVerticaDB():
    host = 'IP or DNS'  # or arg in your .env file os.getenv('host')
    port = 5433
    user = 'user'
    password = 'password'
    data_base = 'DB name'
    read_timeout = 'Read timeout in sec'


class Credentials():
    credentials = 'yours file name.json'


class CityDict():
    city_dict = {'city_phone_code0': ['city_name'],
                 'city_phone_code1': ['city_name']}
    city_gspread_key = {'city_phone_code0': 'Google spread key for cityID 0 in city_dict',
                        'city_phone_code1': 'Google spread key for cityID 1 in city_dict'}

    city_bonus_plan_dict = {
        # each [] = one step in bonus-plan
        'city_phone_code0': [['trips-need', 'bonus', 'previous-bonus'], ['', '', ''], ['', '', '']],
        # starts at max bonus and to min bonus
        'city_phone_code1': [[180, 800, 600], [160, 600, 400], [130, 400, 0]]
    }
