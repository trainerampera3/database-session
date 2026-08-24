
def create(conn):

    with conn.cursor() as cur:
        cur.execute("""
            Create table if not exists trainers(
            trainer_id varchar(10) primary key,
            trainer_name varchar(20))        
    """)

        cur.execute("""
            Create table if not exists branch(
            branch_id varchar(10) primary key,
            branch_name varchar(20)
            )
    """)

        cur.execute("""
        Create table if not exists dietplan(
        diet_id varchar(10) primary key,
        diet_name varchar(20))
    """)

        cur.execute("""
            Create table if not exists goals(
            goal_id varchar(10) primary key,
            goal_name varchar(20)
            )
    """)
        cur.execute("""
            create table if not exists plans(
            plan_id  varchar(10) primary key,
            plan_type varchar(15))
    """)

        cur.execute("""
            create table if not exists customer(
            cust_id varchar(10) primary key,
            fullname varchar(30),
            age int,
            gender varchar(10),
            joindate date,
            expirydate date,
            renewal_status varchar(20),
            trainer_id varchar(10) references trainers(trainer_id),
            branch_id varchar(10) references branch(branch_id),
            goal_id varchar(10) references goals(goal_id),
            plan_id varchar(10) references plans(plan_id),
            diet_id varchar(10) references dietplan(diet_id))
    """)


    conn.commit()
    print('Tables inserted Successfullly')