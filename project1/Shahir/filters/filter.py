import psycopg
from psycopg import sql
from utils.database_connection import connection
class Filter:

    def __init__(self):
        self.conn = psycopg.connect(
            host="localhost",
            port="5433",
            dbname="Practice",
            user="shahir",
            password="shahir"
        )
        self.conn=connection()


    def load_data(self, table_name):
        with self.conn.cursor() as cursor:
            query = sql.SQL("SELECT * FROM {}").format(
                sql.Identifier(table_name)
            )

            cursor.execute(query)
            all_data = cursor.fetchall()

        return all_data
    
    def give_min_max_dates(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                select min(date_of_admission) from patients;
            """)
            min_date=cursor.fetchone()[0]
            cursor.execute("""
                select max(date_of_admission) from patients;
            """)
            max_date=cursor.fetchone()[0]
        return min_date,max_date
    def admission_type(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                select DISTINCT(admission_type) from patients;
            """)
            res= cursor.fetchall()
            lis=[]
            for row in res:
                lis.append(row[0])
            return lis
    def get_medical_condition(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
            select DISTINCT(medical_condition) from patients;
            """)
            res=[]
            for row in cursor.fetchall():
                res.append(row[0])
            return res
    def get_hospital(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                select DISTINCT(hospital) from patients;
            """)
            res=[]
            for row in cursor.fetchall():
                res.append(row[0])
            return res
    def filter(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
            CREATE TEMP TABLE filtered_data AS
            SELECT *
            FROM patients

        """)

            self.conn.commit()

 
    def get_patient_count(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                select count(*) from filtered_data;
            """)
            return cursor.fetchone()[0]
    def get_avg_discharge_rate(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
        
                        select round(avg(discharge_date-date_of_admission ),2) from filtered_data;     

                    """)
            return cursor.fetchone()[0]
    def get_gender_count(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                
                    select gender,count(*) from filtered_data group by gender;
                            """)
            labels = []             
            values = []
            for row in  cursor.fetchall():
                labels.append(row[0])
                values.append(row[1])
            return labels,values

    def get_admissions_by_time(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    EXTRACT(YEAR FROM date_of_admission)::int,
                    COUNT(*)
                FROM filtered_data
                GROUP BY EXTRACT(YEAR FROM date_of_admission)
                ORDER BY EXTRACT(YEAR FROM date_of_admission);
            """)

            labels = []             
            values = []
            for row in  cursor.fetchall():
                labels.append(row[0])
                values.append(row[1])
            return labels,values

    def get_disease_frequency(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
            select medical_condition,count(*) from filtered_data group by medical_condition;
        """)

            labels = []             
            values = []
            for row in  cursor.fetchall():
                labels.append(row[0])
                values.append(row[1])
            return labels,values
    def get_department_frequency(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                select hospital,count(*) from filtered_data group by hospital;
        """)

            labels = []             
            values = []
            for row in  cursor.fetchall():
                labels.append(row[0])
                values.append(row[1])
            return labels,values
    def get_drug_frequency(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                select medication,count(*) from filtered_data group by medication;
        """)

            labels = []             
            values = []
            for row in  cursor.fetchall():
                labels.append(row[0])
                values.append(row[1])
            return labels,values
    def get_total_billing_amount(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                select sum(billing_amount) from filtered_data;
            """)
            return cursor.fetchone()[0]
    def get_admission_type(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
            select admission_type,count(*) from filtered_data group by admission_type;
            """)
            labels=[]
            values=[]
            for row in cursor.fetchall():
                labels.append(row[0])
                values.append(row[1])
            return labels,values