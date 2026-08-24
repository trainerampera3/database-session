import psycopg
import pandas as pd

conn=psycopg.connect(
    host='localhost',
    port='5433',
    dbname='postgres',
    user='shahir',
    password='shahir'
)

'''
#create beds table 
with conn.cursor() as cur:
    cur.execute("""
            CREATE TABLE if not exists beds (
                bed_id INT PRIMARY KEY,
                bed_number VARCHAR(20) NOT NULL,
                bed_status VARCHAR(20) NOT NULL,
                ward_id INT NOT NULL
            )
        """)
    
    beds_data=pd.read_csv('data/hospital_data/bed.csv')
    with cur.copy("""
            copy beds from stdin
    """) as copy:
        for row in beds_data.itertuples(index=False,name=None):
            copy.write_row(row)
    conn.commit()

#create department table

with conn.cursor() as cur:

    cur.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                department_id INT PRIMARY KEY,
                department_name VARCHAR(100) NOT NULL,
                department_type VARCHAR(50) NOT NULL,
                floor_number INT NOT NULL,
                status VARCHAR(20) NOT NULL
            )
        """)
    department_data=pd.read_csv('data/hospital_data/department.csv')
    with cur.copy("""
            copy departments from stdin
    """) as copy:
        for row in department_data.itertuples(index=False,name=None):
            copy.write_row(row)
    conn.commit()



with conn.cursor() as cur:
    cur.execute("""
            CREATE TABLE IF NOT EXISTS diseases (
                disease_id INT PRIMARY KEY,
                disease_name VARCHAR(150) NOT NULL,
                disease_category VARCHAR(100) NOT NULL
            )
        """)
    with cur.copy("""
        copy diseases from stdin 
    """) as copy:
        diseases_data=pd.read_csv('data/hospital_data/disease.csv')
        for row in diseases_data.itertuples(index=False,name=None):
            copy.write_row(row)
    conn.commit()

    
with conn.cursor() as cur:
    cur.execute("""
            CREATE TABLE IF NOT EXISTS wards (
                ward_id INT PRIMARY KEY,
                ward_name VARCHAR(100) NOT NULL,
                ward_type VARCHAR(50) NOT NULL,
                total_beds INT NOT NULL,
                department_id INT NOT NULL,

                FOREIGN KEY (department_id)
                    REFERENCES departments(department_id)
            )
        """) 
    with cur.copy("""
            copy wards from stdin
    
    """) as copy:
        wards=pd.read_csv('data/hospital_data/ward.csv')
        for row in wards.itertuples(index=False,name=None):
            copy.write_row(row)
    
   
    cur.execute("""
            CREATE TABLE IF NOT EXISTS patient_admissions (
                patient_id INT NOT NULL,
                gender VARCHAR(20) NOT NULL,
                date_of_birth DATE NOT NULL,
                blood_group VARCHAR(10) NOT NULL,
                city VARCHAR(100) NOT NULL,
                contact_number VARCHAR(50) NOT NULL,

                admission_id INT PRIMARY KEY,
                admission_date DATE NOT NULL,
                discharge_date DATE,

                admission_type VARCHAR(50) NOT NULL,
                admission_status VARCHAR(50) NOT NULL,

                department_id INT NOT NULL,
                ward_id INT NOT NULL,
                bed_id INT NOT NULL,
                disease_id INT NOT NULL,

                FOREIGN KEY (department_id)
                    REFERENCES departments(department_id),

                FOREIGN KEY (ward_id)
                    REFERENCES wards(ward_id),

                FOREIGN KEY (bed_id)
                    REFERENCES beds(bed_id),

                FOREIGN KEY (disease_id)
                    REFERENCES diseases(disease_id)
            )
        """)
    with cur.copy("""
            copy patient_admissions from stdin
    """) as copy:
        admission_data=pd.read_csv('data/patient_detials.csv')
        for row in admission_data.itertuples(index=False,name=None):
            copy.write_row(row)
    conn.commit()

with conn.cursor() as cur:
    cur.execute("""
            CREATE TABLE IF NOT EXISTS drugs (
                drug_id INT PRIMARY KEY,
                drug_name VARCHAR(100) NOT NULL,
                brand_name VARCHAR(150) NOT NULL,
                drug_category VARCHAR(100) NOT NULL,
                unit_cost DECIMAL(10, 2) NOT NULL,
                manufacturer_id INT NOT NULL
            )
        """)
    drugs=pd.read_csv('data/drug.csv')
    with cur.copy("""
            copy drugs from stdin
    """) as copy:
        for row in drugs.itertuples(index=False,name=None):
            copy.write_row(row)
    conn.commit()
    

with conn.cursor() as cur:
    cur.execute("""
            CREATE TABLE IF NOT EXISTS prescriptions (
                prescription_id INT PRIMARY KEY,
                dosage VARCHAR(50) NOT NULL,
                frequency VARCHAR(50) NOT NULL,
                duration_days INT NOT NULL,
                admission_id INT NOT NULL,
                drug_id INT NOT NULL,

                FOREIGN KEY (admission_id)
                    REFERENCES patient_admissions(admission_id),

                FOREIGN KEY (drug_id)
                    REFERENCES drugs(drug_id)
            )
        """)
    with cur.copy("""
            copy prescriptions from stdin
    """) as copy:
        prescription=pd.read_csv('data/prescription.csv')
        for row in prescription.itertuples(index=False,name=None):
            copy.write_row(row)
    conn.commit()

    '''
with conn.cursor() as cur:

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patient_insurance (
            patient_insurance_id INT PRIMARY KEY,
            policy_number VARCHAR(50) NOT NULL,
            coverage_percentage INT NOT NULL,
            policy_start_date DATE NOT NULL,
            policy_end_date DATE NOT NULL,
            patient_id INT NOT NULL,
            insurance_provider_id INT NOT NULL,
            provider_name VARCHAR(150) NOT NULL,
            provider_type VARCHAR(50) NOT NULL,
            contact_details VARCHAR(20) NOT NULL,
            coverage_limit DECIMAL(12, 2) NOT NULL
        )
    """)
    insurance_data=pd.read_csv('data/insurance.csv')
    with cur.copy("""
        copy patient_insurance from stdin
    """) as copy:
        for row in insurance_data.itertuples(index=False,name=None):
            copy.write_row(row)
    conn.commit()