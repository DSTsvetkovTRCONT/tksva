import os
import psycopg2
from dotenv import load_dotenv
from colorama import Fore
import pandas as pd

basedir = os.path.abspath(os.path.dirname(__file__))

if os.path.exists('.env'):
    load_dotenv(os.path.join(basedir, '.env'))
else:
    load_dotenv(os.path.join(basedir, '.envexample'))



def psql_get_posts(user_id):
    sql = f"""SELECT * FROM post WHERE task_status='в очереди' AND user_id = {user_id}"""
    psql_connection=psycopg2.connect(host=os.environ.get('PSQL_HOST'),
                               port = os.environ.get('PSQL_PORT'),
                               database=os.environ.get('PSQL_DBNAME'),
                               user=os.environ.get('PSQL_USER'),
                               password=os.environ.get('PSQL_PWD'))
    with psql_connection:
        cur = psql_connection.cursor()
        cur.execute(sql)
        df = pd.DataFrame(cur.fetchall(), columns=['id','user_id','form_name','conditions','task_status','file_to_download','task_status_timestamp','timestamp'])    
    return df


def get_queued_posts_qty(user_id):
    sql_own = f"""SELECT count(*) FROM post WHERE (task_status='в очереди' OR task_status LIKE '%загружено%') AND user_id = {user_id}"""
    sql_all = f"""SELECT count(*) FROM post WHERE task_status='в очереди' OR task_status LIKE '%загружено%'"""
    psql_connection=psycopg2.connect(host=os.environ.get('PSQL_HOST'),
                               port = os.environ.get('PSQL_PORT'),
                               database=os.environ.get('PSQL_DBNAME'),
                               user=os.environ.get('PSQL_USER'),
                               password=os.environ.get('PSQL_PWD'))
    with psql_connection:
        cur = psql_connection.cursor()
        cur.execute(sql_own)
        own_queued_posts_qty = cur.fetchone()[0]   
        cur.execute(sql_all)
        all_queued_posts_qty = cur.fetchone()[0]  
    return {'all_queued_posts_qty':all_queued_posts_qty, 'own_queued_posts_qty':own_queued_posts_qty}
        
def is_already_queued(user_id, form_name, conditions):
    sql = f"""SELECT
                user_id,form_name,conditions
            FROM
                post
            WHERE
                user_id =1 and form_name = 'DownloadForRailwayForm' and task_status = 'в очереди'
            """
    psql_connection=psycopg2.connect(host=os.environ.get('PSQL_HOST'),
                               port = os.environ.get('PSQL_PORT'),
                               database=os.environ.get('PSQL_DBNAME'),
                               user=os.environ.get('PSQL_USER'),
                               password=os.environ.get('PSQL_PWD'))        
    with psql_connection:
        cur = psql_connection.cursor()
        cur.execute(sql)
    df = pd.DataFrame(cur.fetchall(), columns=['user_id','form_name','conditions'])
 
    return (len(df[df['conditions']==conditions]))

def file_is_already_ready(user_id, form_name, conditions):
    sql = f"""SELECT
                user_id,form_name,conditions
            FROM
                post
            WHERE
                user_id =1 and form_name = 'DownloadForRailwayForm' and task_status = 'файл сформирован'
            """
    psql_connection=psycopg2.connect(host=os.environ.get('PSQL_HOST'),
                               port = os.environ.get('PSQL_PORT'),
                               database=os.environ.get('PSQL_DBNAME'),
                               user=os.environ.get('PSQL_USER'),
                               password=os.environ.get('PSQL_PWD'))        
    with psql_connection:
        cur = psql_connection.cursor()
        cur.execute(sql)
    df = pd.DataFrame(cur.fetchall(), columns=['user_id','form_name','conditions'])
 
    return (len(df[df['conditions']==conditions]))

def get_dwh_table_info():  
    sql = f"""SELECT table_info FROM dwh_tables_info"""
    try:
        psql_connection=psycopg2.connect(host=os.environ.get('PSQL_HOST'),
                               port = os.environ.get('PSQL_PORT'),
                               database=os.environ.get('PSQL_DBNAME'),
                               user=os.environ.get('PSQL_USER'),
                               password=os.environ.get('PSQL_PWD')) 
        with psql_connection:
            cur = psql_connection.cursor()
            cur.execute(sql)
            return cur.fetchone()[0]
    except:
        return {'railway_names':'', 'station_names':'', 'min_date':'1970-01-01 00:00:00', 'max_date':'1970-01-01 00:00:00'}


def mark_as_downloded(task_id):
    sql = f"""UPDATE
                post
            SET
                task_status = 'файл загружен'
            WHERE
                id={task_id}
                """
    psql_connection=psycopg2.connect(host=os.environ.get('PSQL_HOST'),
                               port = os.environ.get('PSQL_PORT'),
                               database=os.environ.get('PSQL_DBNAME'),
                               user=os.environ.get('PSQL_USER'),
                               password=os.environ.get('PSQL_PWD'))            
                
    with psql_connection:
        cur = psql_connection.cursor()
        cur.execute(sql)

def clear_if_complited(user_id, form_name):
    sql = f"""UPDATE
                post
            SET
                task_status = 'скрыта пользователем'
            WHERE
                user_id = {user_id} and
                form_name = '{form_name}' and 
                task_status = 'файл загружен'
            """
    psql_connection=psycopg2.connect(host=os.environ.get('PSQL_HOST'),
                               port = os.environ.get('PSQL_PORT'),
                               database=os.environ.get('PSQL_DBNAME'),
                               user=os.environ.get('PSQL_USER'),
                               password=os.environ.get('PSQL_PWD'))        
            
    with psql_connection:
        cur = psql_connection.cursor()
        cur.execute(sql)     
   
   
if __name__ == '__main__':
    print(get_dwh_table_info())