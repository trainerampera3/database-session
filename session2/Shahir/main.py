import psycopg

from create_tables import create_tables
from load_data import load_data


conn = psycopg.connect(
    host="localhost",
    port="5433",
    dbname="postgres",
    user="shahir",
    password="shahir"
)

create_tables(conn)

load_data(
    conn,
    "data/hospital_data/department.csv",
    "departments"
)

load_data(
    conn,
    "data/hospital_data/disease.csv",
    "diseases"
)

load_data(
    conn,
    "data/hospital_data/ward.csv",
    "wards"
)

load_data(
    conn,
    "data/hospital_data/bed.csv",
    "beds"
)

load_data(
    conn,
    "data/patient_detials.csv",
    "patient_admissions"
)

load_data(
    conn,
    "data/hospital_data/drug.csv",
    "drugs"
)

load_data(
    conn,
    "data/hospital_data/prescription.csv",
    "prescriptions"
)

load_data(
    conn,
    "data/insurance.csv",
    "patient_insurance"
)

conn.close()