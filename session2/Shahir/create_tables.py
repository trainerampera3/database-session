def create_tables(conn):

    with conn.cursor() as cur:

        # Departments
        cur.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                department_id INT PRIMARY KEY,
                department_name VARCHAR(100) NOT NULL,
                department_type VARCHAR(50) NOT NULL,
                floor_number INT NOT NULL,
                status VARCHAR(20) NOT NULL
            )
        """)

        # Diseases
        cur.execute("""
            CREATE TABLE IF NOT EXISTS diseases (
                disease_id INT PRIMARY KEY,
                disease_name VARCHAR(150) NOT NULL,
                disease_category VARCHAR(100) NOT NULL
            )
        """)

        # Wards
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

        # Beds
        cur.execute("""
            CREATE TABLE IF NOT EXISTS beds (
                bed_id INT PRIMARY KEY,
                bed_number VARCHAR(20) NOT NULL,
                bed_status VARCHAR(20) NOT NULL,
                ward_id INT NOT NULL,

                FOREIGN KEY (ward_id)
                    REFERENCES wards(ward_id)
            )
        """)

        # Patient admissions
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

        # Drugs
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

        # Prescriptions
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

        # Patient insurance
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

    conn.commit()