import os
from dotenv import load_dotenv
from clickhouse_driver import Client

basedir = os.path.abspath(os.path.dirname(__file__))
if os.path.exists('.env'):
    load_dotenv(os.path.join(basedir, '.env'))
else:
    load_dotenv(os.path.join(basedir, '.envexample'))
    
    
print(os.path.join(basedir, '.envexample'))    

class Config:
    # DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-will-never-guess'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'app.db')    
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['dstsvetkovpro@yandex.ru','mob89036177755@gmail.com']   

    connection=Client(host=os.environ.get('CLICK_HOST'),
                  port = os.environ.get('CLICK_PORT'),
                  database=os.environ.get('CLICK_DBNAME'),
                  user=os.environ.get('CLICK_USER'),
                  password=os.environ.get('CLICK_PWD'),
                  secure=True,
                  verify=False) 

    POSTS_PER_PAGE = 3

if __name__ == '__main__':
    print(Config.__dict__)