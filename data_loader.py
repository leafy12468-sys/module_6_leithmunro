import sqlite3
import pandas as pd
from database_ import create_db

def load_csv_to_db(conn, csv_path='csv.csv'):
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        # Seperate timestamp into parts
        time_parts = str(row['timestamp']).split(':')
        hour, minute, second = int(time_parts[0]), int(time_parts[1]), int(time_parts[2])

        # Insert into timestamp_table
        cursor.execute("""
            INSERT INTO timestamp_table (second, minute, hour)
            VALUES (?, ?, ?)
        """, (second, minute, hour))
        timestamp_id = cursor.lastrowid

        # Insert into batch_id_table 
        cursor.execute("""
            INSERT OR IGNORE INTO batch_id_table (batch_id_value)
            VALUES (?)
        """, (int(row['batch_id']),))
        cursor.execute("SELECT batch_id FROM batch_id_table WHERE batch_id_value = ?", (int(row['batch_id']),))
        batch_id = cursor.fetchone()[0]

        # Insert each reading and link in file_table
        for i in range(1, 11):
            reading_value = float(row[f'reading{i}'])

            cursor.execute("""
                INSERT INTO readings (reading_value)
                VALUES (?)
            """, (reading_value,))
            reading_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO file_table (batch_id, reading_id, timestamp_id)
                VALUES (?, ?, ?)
            """, (batch_id, reading_id, timestamp_id))
    try:
        cursor.execute("""
            INSERT INTO valid_table(file_id, filename)
                       VALUES (?, ?, ?)
                       """, (file_id, filename))
        conn.commit()
    except Exception as e:
        cursor.execute("""
            INSERT INTO invalid_table(file_id, filename)
                       VALUES (?, ?, ?)
                       """, (file_id, filename))
        conn.commit()

if __name__ == "__main__":
    conn = sqlite3.connect('my_database.db')
    create_db(conn)
    load_csv_to_db(conn)
    conn.close()