from flask import g
import sqlite3
import uuid
from sqlite3 import Error
from Utilities.Db_utilities import get_db, table_ids

def create_tables_table(conn):
    try:
        sql_create_tables_table = """ CREATE TABLE IF NOT EXISTS tables (
                                        table_index INTEGER PRIMARY KEY,
                                        table_name TEXT
                                    ); """
        if conn is not None:
            conn.execute(sql_create_tables_table)
        else:
            print("Error! could not create tables table")
    except Error as e:
        print(e)

def create_entities_table(conn):
    try:
        sql_create_entities_table = """ CREATE TABLE IF NOT EXISTS entities (
                                        entity_id TEXT PRIMARY KEY,
                                        table_index INTEGER REFERENCES tables(table_index)
                                    ); """
        if conn is not None:
            conn.execute(sql_create_entities_table)
        else:
            print("Error! could not create entities table")
    except Error as e:
        print(e)

def create_users_table(conn):
    try:
        sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                        user_name TEXT,
                                        user_id TEXT PRIMARY KEY,
                                        password TEXT,
                                        FOREIGN KEY (user_id) REFERENCES entities(entity_id) ON DELETE CASCADE
                                    ); """
        if conn is not None:
            conn.execute(sql_create_users_table)
            conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_username ON users(user_name)')
        else:
            print("Error! could not create users table")
    except Error as e:
        print(e)

def create_tasks_table(conn):
    try:
        sql_create_users_table = """ CREATE TABLE IF NOT EXISTS tasks (
                                        task_id TEXT PRIMARY KEY,
                                        task_description TEXT,
                                        FOREIGN KEY (task_id) REFERENCES entities(entity_id) ON DELETE CASCADE
                                    ); """
        if conn is not None:
            conn.execute(sql_create_users_table)
        else:
            print("Error! could not create tasks table")
    except Error as e:
        print(e)

def create_connections_table(conn):
    try:
        sql_create_users_table = """ CREATE TABLE IF NOT EXISTS connections (
                                        source_id TEXT,
                                        dest_id TEXT,
                                        PRIMARY KEY (source_id, dest_id),
                                        FOREIGN KEY (source_id) REFERENCES entities(entity_id) ON DELETE CASCADE,
                                        FOREIGN KEY (dest_id) REFERENCES entities(entity_id) ON DELETE CASCADE
                                    ); """
        if conn is not None:
            conn.execute(sql_create_users_table)
            conn.execute('CREATE INDEX IF NOT EXISTS idx_sources ON connections(source_id)')
        else:
            print("Error! could not create connections table")
    except Error as e:
        print(e)
class Empty:
    pass
def add_tables(conn):
    conn.execute('INSERT OR IGNORE INTO tables(table_index, table_name) VALUES (?,?)', (0, 'users'))
    conn.execute('INSERT OR IGNORE INTO tables(table_index, table_name) VALUES (?,?)', (1, 'tasks'))

    g.table_ids=Empty()
    g.table_ids.users=0
    g.table_ids.tasks=1

def create_tables(conn):
    create_entities_table(conn)
    create_tables_table(conn)
    create_users_table(conn)
    create_tasks_table(conn)
    create_connections_table(conn)
    add_tables(conn)
    conn.commit()
    
def add_task(description, tags):
    try:
        conn = get_db()
        task_id = str(uuid.uuid4())
        conn.execute('BEGIN TRANSACTION')
        conn.execute('INSERT INTO entities(entity_id, table_index) VALUES (?, ?)', (task_id, table_ids.tasks))
        conn.execute('INSERT INTO tasks(task_id, task_description) VALUES (?, ?)', (task_id, description))    
        for tag in tags:
            conn.execute('INSERT INTO connections(source_id, dest_id) VALUES (?, ?)', (tag, task_id))
        conn.commit()
    except:
        conn.rollback()
        raise

def remove_task(task_id):
    conn = get_db()
    sql = ''' DELETE FROM tasks WHERE task_id = ? '''
    cur = conn.cursor()
    n=cur.rowcount
    cur.execute(sql, (task_id,))
    conn.commit()
    m=n-cur.rowcount
    if (m==0): 
        print('delete failed')
        return False
    return True

def get_task(tags):
    conn=get_db()
    cur = conn.cursor()
    tag_count = len(tags)
    sql=f"""
    SELECT tasks.*
    FROM tasks
    JOIN connections ON tasks.task_id = connections.dest_id
    WHERE connections.source_id IN ({', '.join('?' for _ in tags)})
    GROUP BY tasks.task_id
    HAVING COUNT(tasks.task_id) = {tag_count};
    ORDER BY RANDOM()
    LIMIT 1
    """
    sql2 = """
    SELECT tasks.*
    FROM tasks
    JOIN connections ON tasks.task_id = connections.dest_id
    WHERE connections.source_id = ?
    ORDER BY RANDOM()
    LIMIT 1
    """
    cur.execute(sql2, (tags[0],))
    task = cur.fetchone()
    return task

def all_tasks():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()
    return tasks