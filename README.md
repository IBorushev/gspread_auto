# gspread_auto
Manual
1. create GSpread service account(GSSA) and recieve json-token
2. download your json and put into main dir
3. add GSSA to GSpread and allow to change doc
4. set your config.py | find the draft in config_excample.py
5. add your .env file with settings connection to DB | draft in .env_excample
6. create sheet with name 'шаблон'. Script will be copy this sheet

start your script from cmd/bash/terminal<br>
python3 main.py "type" "params"<br>
  "type" - Manual or Auto<br>
  "params"<br>
    --city="city-id:int"  # required parameter<br>
    --week="int"     # default is last week<br>
    --year="int"     # default is 2019<br>
