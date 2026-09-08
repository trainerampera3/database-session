import psycopg as pg 


def get_connection():

    return pg.connect(
        user = 'jayanth',
        dbname='test',
        password='admin@123',
        port=5433,
        host='localhost'
    )