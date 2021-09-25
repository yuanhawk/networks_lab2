from data.server import cache

import json
from types import SimpleNamespace
from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from typing import Optional

db_name = 'students'

# Database Queries
def get_num_of_students(c):
    return c.hlen(db_name)

def insert_student(student, c):
    c.hset(db_name, student['id'], json.dumps(jsonable_encoder(student)))

def upsert_student(id, details, c):
    if c.hexists(db_name, id):
        student = json.loads(c.hget(db_name, id))
        for k1, v1 in details.items():
            for k2 in student.keys():
                if k1 == k2:
                    student[k2] = v1
        insert_student(student, c)
        return student['name'] + ' credentials successfully'
    else:
        if 'id' not in details.keys():
            return 'Student credentials not found'
        insert_student(details, c)
        return details['name'] + ' credentials inserted successfully'

def delete_student_by_id(id, c):
    if c.hexists(db_name, id):
        message = json.loads(c.hget(db_name, id))['name'] + ' credentials deleted successfully'
        c.hdel(db_name, id)
        return message
    return None

def delete_all_students(c):
    c.flushdb()
    if get_num_of_students(c) == 0:
        return True
    return False

def get_student_by_id(id, c):
    if c.hexists(db_name, id):
        return json.loads(c.hget(db_name, id))
    return None

def get_all_students(c, limit: Optional[int] = 10000, start: Optional[int] = 0):
    students = []
    count = 0
    for key in c.scan_iter():
        for k, v in c.hgetall(key).items():
            if len(students) == int(limit):
                return students
            if count >= int(start):
                students.append(json.loads(v))
            count += 1
    return students