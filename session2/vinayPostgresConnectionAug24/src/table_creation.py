from database import get_connection


def create_tables():

    connection = get_connection()
    cursor = connection.cursor()

    # Create tables

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS used_cars (
            usedcarskuid UUID PRIMARY KEY,
            oem VARCHAR(100),
            model VARCHAR(150),
            variant VARCHAR(150),
            myear INTEGER,
            body VARCHAR(50),
            fuel VARCHAR(50),
            transmission VARCHAR(50),
            km NUMERIC,
            owner_type VARCHAR(50),
            city VARCHAR(100),
            state VARCHAR(100),
            utype VARCHAR(50),
            listed_price NUMERIC,
            color VARCHAR(50),
            vehicle_age INTEGER,
            price_segment VARCHAR(50)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_specs (
            usedcarskuid UUID PRIMARY KEY,
            engine_type VARCHAR(100),
            no_of_cylinder NUMERIC,
            turbo_charger BOOLEAN,
            super_charger BOOLEAN,
            length NUMERIC,
            width NUMERIC,
            height NUMERIC,
            wheel_base NUMERIC,
            seats NUMERIC,
            gear_box VARCHAR(50),
            drive_type VARCHAR(50),
            max_power_delivered NUMERIC,
            max_torque_delivered NUMERIC,
            FOREIGN KEY (usedcarskuid)
                REFERENCES used_cars(usedcarskuid)
                ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            usedcarskuid UUID PRIMARY KEY,
            price_lakhs NUMERIC,
            km_thousands NUMERIC,
            myear INTEGER,
            vehicle_age INTEGER,
            city VARCHAR(100),
            state VARCHAR(100),
            oem VARCHAR(100),
            model VARCHAR(150),
            fuel VARCHAR(50),
            transmission VARCHAR(50),
            body VARCHAR(50),
            owner_type VARCHAR(50),
            utype VARCHAR(50),
            price_segment VARCHAR(50),
            FOREIGN KEY (usedcarskuid)
                REFERENCES used_cars(usedcarskuid)
                ON DELETE CASCADE
        )
    """)

    connection.commit()

    cursor.close()
    connection.close()

    print("Tables created successfully.")


if __name__ == "__main__":
    create_tables()