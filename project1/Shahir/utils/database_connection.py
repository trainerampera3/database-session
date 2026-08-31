import pandas as pd
import psycopg
import csv
import logging
from datetime import timedelta


def connection():
    conn = psycopg.connect(
    host="localhost",
    port="5433",
    dbname="Practice",
    user="shahir",
    password="shahir"
)
    return conn