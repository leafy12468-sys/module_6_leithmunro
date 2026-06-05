import sqlite3
import pytest

from database_ import create_db

@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    create_db(connection)
    yield connection
    connection.close()
    
@pytest.mark.parametrize("second, minute, hour", [
    (59, 0, 0),
    (0, 30, 0),
    (0, 0, 22),
])  

#   creates temperory database for testing
def test_valid_time_insert(conn, second, minute, hour):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO timestamp_table (second, minute, hour)
        VALUES (?, ?, ?)
        """, (second, minute, hour))
    conn.commit()
    
    cursor.execute("SELECT second, minute, hour FROM timestamp_table")
    row = cursor.fetchone()
    assert row == (second, minute, hour)

@pytest.mark.parametrize("second, minute, hour", [
    (-1, 0, 0),
    (0, 90, 0),
    (0, 0, 300),
])

def test_invalid_time_insert(conn, second, minute, hour):
    cursor = conn.cursor()
    with pytest.raises(Exception):
        cursor.execute("""
            INSERT INTO timestamp_table (second, minute, hour)
            VALUES (?, ?, ?)
            """, (second, minute, hour))
        conn.commit()

    cursor.execute("SELECT second, minute, hour FROM timestamp_table")
    row = cursor.fetchone()
    assert row is None

@pytest.mark.parametrize("batch_id_value", [ 
    1, 2, 3
])
def test_invalid_batch_id(conn, batch_id_value):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO batch_id_table(batch_id_value)
        VALUES (?)
    """, (batch_id_value,))
    conn.commit()

    with pytest.raises(Exception):
        cursor.execute("""
            INSERT INTO batch_id_table(batch_id_value)
            VALUES (?)
        """, (batch_id_value,))
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM batch_id_table")
    count = cursor.fetchone()
    assert count == (1,)

@pytest.mark.parametrize("batch_id_value", [ 
    1, 2, 3
])
def test_valid_batch_id(conn, batch_id_value):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO batch_id_table(batch_id_value)
        VALUES (?)
    """, (batch_id_value,))
    conn.commit()

@pytest.mark.parametrize("batch_id, reading_id, time_id", [
    (1, 2, 3)
])
def test_valid_file_ids(conn, batch_id, reading_id, time_id):
    cursor = conn.cursor()

    cursor.execute("INSERT INTO batch_id_table(batch_id) VALUES (?)", (batch_id,))
    cursor.execute("INSERT INTO readings(reading_id) VALUES (?)", (reading_id,))
    cursor.execute("INSERT INTO timestamp_table(time_id) VALUES (?)", (time_id,))
    conn.commit()

    cursor.execute("""
        INSERT INTO file_table (batch_id, reading_id, timestamp_id)
        VALUES (?, ?, ?)
    """, (batch_id, reading_id, time_id))
    conn.commit()

    cursor.execute("SELECT batch_id, reading_id, timestamp_id FROM file_table")
    row = cursor.fetchone()
    assert row == (batch_id, reading_id, time_id)

@pytest.mark.parametrize("batch_id, reading_id, time_id, second, minute, hour", [
    (1, 1, 1, 15, 20, 23) 
])

def test_valid_times_with_valid_ids(conn, batch_id, reading_id, time_id, second, minute, hour):
    cursor = conn.cursor()

    cursor.execute("INSERT INTO batch_id_table(batch_id) VALUES (?)", (batch_id,))
    cursor.execute("INSERT INTO readings(reading_id) VALUES (?)", (reading_id,))
    
    cursor.execute(
        "INSERT INTO timestamp_table(time_id, second, minute, hour) VALUES (?, ?, ?, ?)",
        (time_id, second, minute, hour)
    )

    cursor.execute("""
        INSERT INTO file_table (batch_id, reading_id, timestamp_id)
        VALUES (?, ?, ?)
    """, (batch_id, reading_id, time_id))

    conn.commit()

    cursor.execute("SELECT batch_id, reading_id, timestamp_id FROM file_table")
    row = cursor.fetchone()
    assert row == (batch_id, reading_id, time_id)

    cursor.execute(
        "SELECT second, minute, hour FROM timestamp_table WHERE time_id = ?",
        (time_id,)
    )
    time_row = cursor.fetchone()
    assert time_row == (second, minute, hour)


