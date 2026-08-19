create table employee
(emp_id int primary key,
firstname varchar(50) not null,
lastname varchar(50) not null,
department varchar(50),
salary numeric(10,2) check (salary >= 0),
join_date date default CURRENT_DATE);

insert into employee (emp_id, firstname, lastname, department, salary)
values
(101, 'John','smith','HR',45000),
(102, 'Emma','Johnson','Finance',55000),
(103, 'Liam','Brown','IT',68000),
(104, 'Olivia','davis','Marketing',52000),
(105,'noah','Wilson','Sales', 48000);


select * from employee