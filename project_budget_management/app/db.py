import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """Create a table from the create_table_sql statement"""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def main():
    database = "project_budget_management.db"

    sql_create_projects_table = """
    CREATE TABLE IF NOT EXISTS projects (
        id integer PRIMARY KEY,
        name text NOT NULL,
        manager text,
        client text,
        start_date text,
        end_date text,
        first_draft_date text,
        event_location text,
        final_draft_date text
    );"""

    sql_create_budget_items_table = """
    CREATE TABLE IF NOT EXISTS budget_items (
        id integer PRIMARY KEY,
        project_id integer NOT NULL,
        category text,
        subcategory text,
        item text,
        quantity integer,
        unit text,
        days integer,
        unit_spec1 text,
        times integer,
        unit_spec2 text,
        price real,
        allocated_budget real,
        actual_cost real,
        FOREIGN KEY (project_id) REFERENCES projects (id)
    );"""

    sql_create_logs_table = """
    CREATE TABLE IF NOT EXISTS logs (
        id integer PRIMARY KEY,
        project_id integer NOT NULL,
        action text NOT NULL,
        timestamp text NOT NULL,
        details text,
        FOREIGN KEY (project_id) REFERENCES projects (id)
    );"""

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_projects_table)
        create_table(conn, sql_create_budget_items_table)
        create_table(conn, sql_create_logs_table)
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()
