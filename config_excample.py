# class Config:
#    SECRET_KEY = ''
# class Connect_to_VerticaDB(Config):

class Connect_to_VerticaDB():
    host='IP or DNS'
    port= 5433
    user= 'user'
    password= 'password'
    data_base= 'DB name'
    read_timeout= 'Read timeout in sec'

class _Credentials():
    credentials = 'yours file name.json'

class _City_dict():
    city_dict= {'0' : ['city_name', 'city_phone_code'],
                '1' : ['city_name', 'city_phone_code']}
    city_gspread_key = {'0' : 'Google spread key for cityID 0 in city_dict',
                        '1' : 'Google spread key for cityID 1 in city_dict'}
