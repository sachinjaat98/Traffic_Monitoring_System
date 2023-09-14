import pymysql
from sqlalchemy import create_engine,sql
import pandas as pd
from time import sleep

data = pd.read_csv('stats.csv', encoding='latin-1')

# create sqlalchemy engine
engine = create_engine("mysql+pymysql://{user}:{pw}@instance.ctbnhz2jjfor.ap-south-1.rds.amazonaws.com:3306/{db}".format(user="admin", pw="deep1234", db="stats"))
print('Uploading started...')

while True:

    data = pd.read_csv('stats.csv', encoding='latin-1')
    data.to_sql('counts', con = engine, if_exists='replace', chunksize = 1000)
    sleep(20)

