from flask import Blueprint
from flask_login import current_user, login_required
from Utilities.Db_utilities import table_ids
from sqlite3 import Error

def create_tasks_table(i, conn):
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
    conn.execute('INSERT OR IGNORE INTO tables(table_index, table_name) VALUES (?,?)', (i, 'tasks'))
    conn.commit()
    table_ids.tasks=i


todo = Blueprint('Todo', __name__)
from . import routes

@todo.before_request
def require_login():
    if not current_user.is_authenticated:
        return login_required()