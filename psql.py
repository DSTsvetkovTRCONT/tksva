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
   
def get_post(post_id):
    #logger.info('Запущено: get_post. Получаем информацию о посте')

    #try:
        psql_connection = psycopg2.connect(host=os.environ.get('PSQL_HOST'),
                                           port=os.environ.get('PSQL_PORT'),
                                           database=os.environ.get('PSQL_DBNAME'),
                                           user=os.environ.get('PSQL_USER'),
                                           password=os.environ.get('PSQL_PWD'))

        sql = f"""SELECT * FROM post WHERE id={post_id}"""
        with psql_connection:
            cur = psql_connection.cursor()
            cur.execute(sql)
            post_list = cur.fetchone()

        return {'user_id': post_list[1],
                'conditions': post_list[3],
                'task_status': post_list[4],
                'file_to_download': post_list[5]}
    #except Exception:
    #    logger.exception("Не удалось получить информацию о посте")

def get_gives_information_status(dwh_table_name):
    #logger.info(f"Запущено: get_gives_information_status. "
    #            f"Получаем статусы для {dwh_table_name}")

    try:
        psql_connection = psycopg2.connect(host=os.environ.get('PSQL_HOST'),
                                           port=os.environ.get('PSQL_PORT'),
                                           database=os.environ.get('PSQL_DBNAME'),
                                           user=os.environ.get('PSQL_USER'),
                                           password=os.environ.get('PSQL_PWD'))

        with psql_connection:
            cur = psql_connection.cursor()
            cur.execute(f"""SELECT
                                wants_to_refresh,
                                gives_information
                        FROM
                            dwh_tables_info
                        WHERE
                            dwh_table_name = '{dwh_table_name}'""")
            res_list = cur.fetchone()
        res_dict = {'wants_to_refresh': res_list[0],
                    'gives_information': res_list[1]}
        return res_dict
    except Exception:
        #logger.exception("Не удалось получить статусы")
        return False


def set_task_status(post_id, task_status):
    #logger.info(f"Запущено: set_task_status. "
    #            f"Прописываем статус для {post_id} - {task_status}")

    try:
        psql_connection = psycopg2.connect(host=os.environ.get('PSQL_HOST'),
                                           port=os.environ.get('PSQL_PORT'),
                                           database=os.environ.get('PSQL_DBNAME'),
                                           user=os.environ.get('PSQL_USER'),
                                           password=os.environ.get('PSQL_PWD'))

        with psql_connection:
            cur = psql_connection.cursor()
            cur.execute(f"""UPDATE
                                post
                        SET
                            task_status ='{task_status}',
                            task_status_timestamp = now()
                        WHERE
                            id = {post_id}""")
    except Exception:
        #logger.exception("Не удалось прописать статус")
        return False
    return True


def set_gives_information_status(dwh_table_name, status):
    #logger.info(f"Запущено: set_dwh_tables_info_status. "
    #            f"Прописываем для {dwh_table_name} статус {status}")

    #try:
        psql_connection = psycopg2.connect(host=os.environ.get('PSQL_HOST'),
                                           port=os.environ.get('PSQL_PORT'),
                                           database=os.environ.get('PSQL_DBNAME'),
                                           user=os.environ.get('PSQL_USER'),
                                           password=os.environ.get('PSQL_PWD'))
        with psql_connection:
            cur = psql_connection.cursor()
            cur.execute(f"""UPDATE
                            dwh_tables_info
                        SET
                            gives_information = {status},
                            gives_information_timestamp = now()
                        WHERE
                            dwh_table_name = '{dwh_table_name}'""")

        return True
    #except Exception:
    #    logger.exception("Не удалось прописать статус")
    #    return False


if __name__ == '__main__':
    print(get_dwh_table_info())