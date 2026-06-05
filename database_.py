import sqlite3

def create_db(conn):
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS timestamp_table (
        time_id INTEGER PRIMARY KEY,
        second INTEGER CHECK(second BETWEEN 0 AND 59),
        minute INTEGER CHECK(minute BETWEEN 0 AND 59),
        hour INTEGER CHECK(hour BETWEEN 0 AND 23)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS batch_id_table (
        batch_id INTEGER PRIMARY KEY,
        batch_id_value INTEGER UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS readings (
        reading_id INTEGER PRIMARY KEY,
        reading_number INTEGER
        reading_value REAL CHECK(reading_value BETWEEN 0 AND 9.9)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS file_table (
        file_id INTEGER PRIMARY KEY,
        batch_id INTEGER,
        reading_id INTEGER,
        timestamp_id INTEGER,
        FOREIGN KEY (batch_id) REFERENCES batch_id_table(batch_id),
        FOREIGN KEY (reading_id) REFERENCES readings(reading_id),
        FOREIGN KEY (timestamp_id) REFERENCES timestamp_table(time_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS valid_files (
                   file_id INTEGER,
                   filename STRING,
                   FOREIGN KEY (file_id) REFRENCES file_table(file_id) 
                   )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invalid_files (
                   file_id INTEGER,
                   filename STRING,
                   FOREIGN KEY (file_id) REFRENCES file_table(file_id) 
                   )""")

    conn.commit()