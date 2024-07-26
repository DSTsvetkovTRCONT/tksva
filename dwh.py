from clickhouse_driver import Client
import os
from dotenv import load_dotenv
from colorama import Fore

basedir = os.path.abspath(os.path.dirname(__file__))

if os.path.exists('.env'):
    load_dotenv(os.path.join(basedir, '.env'))
else:
    load_dotenv(os.path.join(basedir, '.envexample'))

connection=Client(host=os.environ.get('CLICK_HOST'),
                  port = os.environ.get('CLICK_PORT'),
                  database=os.environ.get('CLICK_DBNAME'),
                  user=os.environ.get('CLICK_USER'),
                  password=os.environ.get('CLICK_PWD'),
                  secure=True,
                  verify=False)
    
def rows_in_download_for_railway(railway_name, start_date, finish_date):
    click_table = os.environ.get('CLICK_TABLE')
    sql = f"SELECT count(*) FROM audit.sales__execution_orders WHERE railway_from_name='{railway_name}' AND datetime_move_started BETWEEN '{start_date}' AND '{finish_date}'	"
    # print(sql)
    with connection:
        return connection.execute(sql)[0][0]   
    
def rows_in_download_for_station(station_name, start_date, finish_date):
    click_table = os.environ.get('CLICK_TABLE')
    sql = f"SELECT count(*) FROM audit.sales__execution_orders WHERE station_from_name='{station_name}' AND datetime_move_started BETWEEN '{start_date}' AND '{finish_date}'	"
    # print(sql)
    with connection:
        return connection.execute(sql)[0][0]       
'''
def get_dwh_table_info():  
    
    click_table = os.environ.get('DWH_TABLE')
    
    sql = f"""SELECT
                min(`SVOD.Дата отправки`) AS min_date,
                max(`SVOD.Дата отправки`) AS max_date,
                arrayStringConcat(arraySort(groupArray(DISTINCT `Дор. Отправления`)),'|') AS railway_names,
                arrayStringConcat(arraySort(groupArray(DISTINCT `Ст. Отправления`)),'|') AS station_names
            FROM
                {click_table}"""
    # print(sql)
    with connection:
        table_info = connection.execute(sql)
   
    return {'min_date':table_info[0][0], 'max_date':table_info[0][1], 'railway_names':table_info[0][2], 'station_names':table_info[0][3]}     
'''    
if __name__ == "__main__":
    print(get_dwh_table_info())
    
