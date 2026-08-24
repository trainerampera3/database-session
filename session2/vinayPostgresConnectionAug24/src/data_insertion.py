import pandas as pd
from database import get_connection


CSV_PATH = "data/used_cars_cleaned.csv"


def insert_data():

    df = pd.read_csv(CSV_PATH)

    connection = get_connection()
    cursor = connection.cursor()

    # Insert data

    used_cars_query = """
        INSERT INTO used_cars (
            usedcarskuid,
            oem,
            model,
            variant,
            myear,
            body,
            fuel,
            transmission,
            km,
            owner_type,
            city,
            state,
            utype,
            listed_price,
            color,
            vehicle_age,
            price_segment
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s
        )
    """

    used_cars_data = df[
        [
            "usedcarskuid",
            "oem",
            "model",
            "variant",
            "myear",
            "body",
            "fuel",
            "transmission",
            "km",
            "owner_type",
            "city",
            "state",
            "utype",
            "listed_price",
            "color",
            "vehicle_age",
            "price_segment"
        ]
    ].itertuples(index=False, name=None)

    cursor.executemany(used_cars_query, used_cars_data)

    vehicle_specs_query = """
        INSERT INTO vehicle_specs (
            usedcarskuid,
            engine_type,
            no_of_cylinder,
            turbo_charger,
            super_charger,
            length,
            width,
            height,
            wheel_base,
            seats,
            gear_box,
            drive_type,
            max_power_delivered,
            max_torque_delivered
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s
        )
    """

    vehicle_specs_data = df[
        [
            "usedcarskuid",
            "engine_type",
            "no_of_cylinder",
            "turbo_charger",
            "super_charger",
            "length",
            "width",
            "height",
            "wheel_base",
            "seats",
            "gear_box",
            "drive_type",
            "max_power_delivered",
            "max_torque_delivered"
        ]
    ].itertuples(index=False, name=None)

    cursor.executemany(vehicle_specs_query, vehicle_specs_data)

    market_data_query = """
        INSERT INTO market_data (
            usedcarskuid,
            price_lakhs,
            km_thousands,
            myear,
            vehicle_age,
            city,
            state,
            oem,
            model,
            fuel,
            transmission,
            body,
            owner_type,
            utype,
            price_segment
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
    """

    market_data = df[
        [
            "usedcarskuid",
            "price_lakhs",
            "km_thousands",
            "myear",
            "vehicle_age",
            "city",
            "state",
            "oem",
            "model",
            "fuel",
            "transmission",
            "body",
            "owner_type",
            "utype",
            "price_segment"
        ]
    ].itertuples(index=False, name=None)

    cursor.executemany(market_data_query, market_data)

    connection.commit()

    cursor.close()
    connection.close()

    print("Data inserted successfully.")


if __name__ == "__main__":
    insert_data()