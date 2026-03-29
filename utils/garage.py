import sqlite3
import pandas as pd
import os

DB_PATH = "drivewise_garage.db"


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS garage (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            saved_at        TEXT DEFAULT (datetime('now','localtime')),
            route           TEXT,
            engine_type     TEXT,
            drive_type      TEXT,
            tire_condition  TEXT,
            cylinders       INTEGER,
            displacement    REAL,
            weight          INTEGER,
            hp              INTEGER,
            accel           REAL,
            base_mpg        REAL,
            adjusted_mpg    REAL,
            monthly_cost    REAL,
            annual_cost     REAL,
            co2_lbs         REAL,
            efficiency_score INTEGER,
            monthly_miles   INTEGER,
            fuel_price      REAL
        )
    """)
    conn.commit()
    return conn


def save_vehicle(name: str, route: str, vehicle: dict,
                 fuel: dict, metrics: dict) -> None:
    conn = _get_conn()
    conn.execute("""
        INSERT INTO garage
        (name, route, engine_type, drive_type, tire_condition,
         cylinders, displacement, weight, hp, accel,
         base_mpg, adjusted_mpg, monthly_cost, annual_cost,
         co2_lbs, efficiency_score, monthly_miles, fuel_price)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        name, route,
        vehicle.get("engine_type","Gasoline"),
        vehicle.get("drive_type","FWD"),
        vehicle.get("tire_condition","New / Optimal"),
        vehicle["cylinders"], vehicle.get("displacement", 2.0),
        vehicle["weight"], vehicle["hp"], vehicle["accel"],
        metrics["base_mpg"], metrics["adjusted_mpg"],
        metrics["fuel_cost"], metrics["annual_cost"],
        metrics["co2_lbs"], metrics["efficiency_score"],
        fuel["monthly_miles"], fuel["fuel_price"],
    ))
    conn.commit()
    conn.close()


def load_garage() -> pd.DataFrame:
    conn = _get_conn()
    df = pd.read_sql_query(
        "SELECT * FROM garage ORDER BY saved_at DESC", conn
    )
    conn.close()
    return df


def delete_vehicle(row_id: int) -> None:
    conn = _get_conn()
    conn.execute("DELETE FROM garage WHERE id=?", (row_id,))
    conn.commit()
    conn.close()


def clear_garage() -> None:
    conn = _get_conn()
    conn.execute("DELETE FROM garage")
    conn.commit()
    conn.close()


def export_csv() -> bytes:
    df = load_garage()
    return df.to_csv(index=False).encode("utf-8")
