from data.server import cache

import json
from types import SimpleNamespace
from fastapi import Depends

db_name = 'students'

# Database instance

# Database Queries
def insert_student(student, c):
    c.lpush(db_name, json.dumps(student))

def update_student():
    pass

def delete_student():
    pass

def delete_all_students(c):
    c.flushdb()
    if len(get_all_students(c)) == 0:
        return True
    return False

def get_student_by_id(id, c):
    for student in c.get(db_name):
        print(student)
        if student['id'] == id:
            return student
    return None

def get_all_students(c):
    return c.lrange(db_name, 0, -1)

def get_list_all_students(c):
    students = []
    for student in get_all_students(c):
        students.append(json.loads(student))
    return students