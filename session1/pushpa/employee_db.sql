
CREATE TABLE employee_details (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    user_name VARCHAR(50) UNIQUE NOT NULL,
    email_address VARCHAR(100) NOT NULL,
    team VARCHAR(50),
    position VARCHAR(50),
    monthly_salary NUMERIC(10,2),
    contact_number VARCHAR(15),
    date_joined DATE
);

INSERT INTO employee_details 
(full_name, user_name, email_address, team, position, monthly_salary, contact_number, date_joined)
VALUES
('Karthik', 'karthik01', 'karthik@gmail.com', 'Development', 'Backend Developer', 55000.00, '9123456780', '2025-06-12'),
('Sneha', 'sneha02', 'sneha@gmail.com', 'Testing', 'QA Engineer', 48000.00, '9234567810', '2025-07-18'),
('Vikram', 'vikram03', 'vikram@gmail.com', 'Sales', 'Sales Executive', 38000.00, '9345678120', '2025-08-25'),
('Ananya', 'ananya04', 'ananya@gmail.com', 'Design', 'UI Designer', 45000.00, '9456781230', '2025-09-10'),
('Rohit', 'rohit05', 'rohit@gmail.com', 'Development', 'Frontend Developer', 52000.00, '9567812340', '2025-10-05');


ALTER TABLE employee_details
ADD COLUMN gender VARCHAR(10);

UPDATE employee_details
SET gender = 'Male'
WHERE id = 1;

UPDATE employee_details
SET gender = 'Female'
WHERE id = 2;

UPDATE employee_details
SET gender = 'Male'
WHERE id = 3;

UPDATE employee_details
SET gender = 'Female'
WHERE id = 4;

UPDATE employee_details
SET gender = 'Male'
WHERE id = 5;

select * from employee_details;


