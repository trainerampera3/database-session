from pathlib import Path

data_path = Path(__file__).parent / "data" / "cleaned"

attendance_data = data_path / "attendance-cleaned.csv"

department_data = data_path / "department-cleaned.csv"

employee_data = data_path / "employees-cleaned.csv"

payroll_data = data_path / "payroll-cleaned.csv"

performance_data = data_path / "performance-cleaned.csv"

from database.connection import create_connection

conn = create_connection()

crs = conn.cursor()

create_departments="""
CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT NOT NULL,
    LOCATION TEXT
    );"""
    
crs.execute(create_departments)
conn.commit()



# 1. Create the Employees Table
create_employees = """
CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY,
    employee_code TEXT UNIQUE,
    gender TEXT,
    age INTEGER,
    department_id INTEGER,
    job_title TEXT,
    join_date TEXT,
    salary REAL,
    email TEXT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);"""

# 2. Create the Attendance Table
create_attendance = """
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY,
    employee_id INTEGER,
    date TEXT,
    status TEXT,
    hours_worked REAL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);"""

# 3. Create the Payroll Table
create_payroll = """
CREATE TABLE IF NOT EXISTS payroll (
    payroll_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    pay_month TEXT,
    salary REAL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);"""

# 4. Create the Performance Table
create_performance = """
CREATE TABLE IF NOT EXISTS performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    rating REAL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);"""

# Execute and commit all definitions
for table_query in [create_employees, create_attendance, create_payroll, create_performance]:
    crs.execute(table_query)
    
conn.commit()
print("All data tables created successfully!")
