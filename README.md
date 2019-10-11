# gspread_auto
Manual
1. create GSpread service account(GSSA) and recieve json-token
2. download your json and put into main dir
3. add GSSA to GSpread and allow to change doc
4. set your config.py | find the draft in config_excample.py
5. add your .env file with settings connection to DB | draft in .env_excample
6. create sheet with name 'шаблон'. Script will be copy this sheet

start your script from cmd/bash/terminal
python3 main.py <type> <params>
  <type> - Manual or Auto
  <params>
    --city=<city-id:int>  # required parameter
    --week=<int>     # default is last week
    --year=<int>     # default is 2019
