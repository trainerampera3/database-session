from pathlib import Path

data_path = Path(__file__).parent / "data" / "cleaned"

attendance_data = data_path / "attendance-cleaned.csv"

department_data = data_path / "department-cleaned.csv"

employee_data = data_path / "employees-cleaned.csv"

payroll_data = data_path / "payroll-cleaned.csv"

performance_data = data_path / "performance-cleaned.csv"

from connection import create_connection

conn = create_connection()

crs = conn.cursor()

create_departments = """
CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY,
    department_name VARCHAR(255) NOT NULL,
    location VARCHAR(255)
);"""

crs.execute(create_departments)
conn.commit()

create_employees = """
CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY,
    employee_code VARCHAR(50) UNIQUE,
    gender VARCHAR(20),
    age INTEGER,
    department_id INTEGER,
    job_title VARCHAR(255),
    join_date DATE,
    salary NUMERIC(12, 2),
    email VARCHAR(255),
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);"""


create_attendance = """
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY,
    employee_id INTEGER,
    date DATE,
    status VARCHAR(50),
    hours_worked NUMERIC(4, 2),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);"""


create_payroll = """
CREATE TABLE IF NOT EXISTS payroll (
    payroll_id INTEGER PRIMARY KEY,
    employee_id INTEGER,
    pay_month VARCHAR(20),
    net_salary NUMERIC(12, 2),
    bonus NUMERIC(12, 2),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);"""


create_performance = """
CREATE TABLE IF NOT EXISTS performance_reviews (
    review_id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    rating NUMERIC(3, 2),
    remarks TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);"""


for table_query in [create_employees, create_attendance, create_payroll, create_performance]:
    crs.execute(table_query)
    
conn.commit()
print("All data tables created successfully!")

