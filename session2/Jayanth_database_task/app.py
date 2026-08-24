import psycopg as pg
import pandas as pd
from createtab import create
from insertval import insert



df = pd.read_csv('./data/Enhanced_Gym_Dataset_10000.csv')
conn = pg.connect(
    host='localhost',
    port='5433',
    dbname='dashboard',
    user='jayanth',
    password='admin@123'
)


print('Connection established Successfully')

create(conn)
insert(conn)

conn.close()


