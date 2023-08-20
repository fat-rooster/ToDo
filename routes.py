from . import todo
from flask import render_template, redirect, url_for, request
from flask_login import current_user
from .backend import add_task, get_task, remove_task, all_tasks

@todo.route('/', methods=['GET'])
def empty_request():
    if current_user.is_authenticated:
        return render_template('task_page.html')
    return redirect(url_for('login_page'))

@todo.route('/submit_task', methods=['GET'])
def submit_task():
    return render_template('submit_task.html')

@todo.route('/all_tasks', methods = ['GET'])
def get_all_tasks():
    tasks = all_tasks()
    return render_template('all_tasks.html', tasks=tasks)

@todo.route('/api/submit_task', methods=['POST'])
def submit_task_api():
    add_task(request.form['description'], [current_user.id])
    return '', 204

@todo.route('/api/get_task')
def supply_random_task():
    task=get_task([current_user.id])
    return task

@todo.route('/api/clear_task/<task_id>', methods=['DELETE'])
def clear_task_api(task_id):
    remove_task(task_id)
    return '', 204

@todo.route('/api/get_all')
def supply_all_tasks():
    return all_tasks()