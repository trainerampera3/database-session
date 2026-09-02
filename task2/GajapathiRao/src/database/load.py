from pathlib import Path
import pandas as pd
from connection import create_connection

# data_path = Path(__file__).parent / "data" / "cleaned"

# attendance_data = data_path / "attendance-cleaned.csv"
# department_data = data_path / "department-cleaned.csv"
# employee_data = data_path / "employees-cleaned.csv"
# payroll_data = data_path / "payroll-cleaned.csv"
# performance_data = data_path / "performance-cleaned.csv"

from app import attendance_data, department_data, employee_data, payroll_data, performance_data

# import attendance_data , department_data, employee_data, payroll_data, performance_data from app
conn = create_connection()
crs = conn.cursor()

def load_csv_to_db(csv_file, table_name):
    """Load data from a CSV file into PostgreSQL, cleaning the employee__id header if present."""
    try:
        
        df_headers = pd.read_csv(csv_file, nrows=0)
        
        columns = list(df_headers.columns)
        if "employee__id" in columns:
            columns = [col.replace("employee__id", "employee_id") for col in columns]
            
        columns_str = ", ".join(columns)
        copy_sql = f"COPY {table_name} ({columns_str}) FROM STDIN WITH CSV HEADER"
        
        with open(csv_file, "r", encoding="utf-8") as f:
            with crs.copy(copy_sql) as copy:
                copy.write(f.read())
                
        conn.commit()
        print(f"Data from {csv_file.name} loaded successfully.")
        
    except Exception as exc:
        conn.rollback()
        print(f" Error loading data from {csv_file.name}: {exc}")



load_csv_to_db(department_data, "departments")
load_csv_to_db(employee_data, "employees")
load_csv_to_db(attendance_data, "attendance")
load_csv_to_db(payroll_data, "payroll") 
load_csv_to_db(performance_data, "performance_reviews")


crs.close()
conn.close()
