from model.student import *
from model.log import Message
from biz.db import *
from data.server import *

from fastapi import Depends, status
from fastapi.responses import JSONResponse

from typing import Optional

# GET methods
@app.get('/')
def read_root(c: Redis = Depends(cache)):
    return 'Welcome To Model Student Page'

@app.get('/students')
def read_root(c: Redis = Depends(cache)):
    if get_num_of_students(c) == 0:
        return 'Students list is empty, please add new students'
    return get_all_students(c)

@app.get('/students/sort/{sortBy}')
def get_students_by_sort_param(sortBy: Optional[str] = None, c: Redis = Depends(cache)):
    if get_num_of_students(c) == 0:
        return 'Students list is empty, please add new students'
    if sortBy == 'id':
        return sorted(get_all_students(c), key=lambda d: int(d['id']))
    elif sortBy == 'name':
        return sorted(get_all_students(c), key=lambda d: str(d['name']))
    elif sortBy == 'gpa':
        student_list = filter(lambda d: d['gpa'] != None, get_all_students(c))
        return sorted(student_list, key=lambda d: float(d['gpa']))
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'message': 'Student list not found'})

@app.get('/students/count/{count}')
def get_students_by_limit(count, c: Redis = Depends(cache)):
    if get_num_of_students(c) == 0:
        return 'Students list is empty, please add new students'
    return get_all_students(c, limit=count)

@app.get('/students/offset/{offset}')
def get_students_by_offset(offset, c: Redis = Depends(cache)):
    if get_num_of_students(c) == 0:
        return 'Students list is empty, please add new students'
    if int(offset) > get_num_of_students(c):
        return []
    return get_all_students(c, start=offset)

@app.get(
    '/students/find/{student_id}',
    responses={
        200: {
            'content': Student,
            'description': 'Return student details'
        },
        404: {'model': Message}
    }
)
async def find_student(student_id: str, c: Redis = Depends(cache)):
    if get_student_by_id(student_id, c) is not None:
        return JSONResponse(status_code=status.HTTP_200_OK, content=get_student_by_id(student_id, c))
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'message': 'Student detail not found'})


# POST methods
@app.post('/students/postsingle')
def create_student(student: Student, c: Redis = Depends(cache)):
    return upsert_student(student.id, dict(student), c)

@app.post('/students/postmultiple')
def create_students(students: List[Student], c: Redis = Depends(cache)):
    response = []
    for s in students:
        upsert_student(s.id, dict(s), c)
        response.append(s.name + ' credentials created')
    return JSONResponse(status_code=status.HTTP_200_OK, content={'message': '; '.join(response)})


# DELETE methods
@app.delete(
    '/students/delete/{id}',
    responses = {
        200: {'model': Message},
        404: {'model': Message}
    }
)
def remove_student_by_id(id: str, c: Redis = Depends(cache)):
    message = delete_student_by_id(id, c)
    if message is not None:
        return JSONResponse(status_code=status.HTTP_200_OK, content={'message': message})
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'message': 'Student ' + id + ' not found'})

@app.delete(
    '/students/deleteall',
    responses={
        200: {
            'content': list,
            'description': 'Return student list'
        },
        404: {'model': Message}
    }
)
def remove_all(c: Redis = Depends(cache)):
    if delete_all_students(c):
        return JSONResponse(status_code=status.HTTP_200_OK, content={'message': 'Students list is cleared'})
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'message': 'Students list not found'})

# PUT method
@app.put(
    '/students/update/{id}',
    responses={
        200: {'model': Message},
        404: {'model': Message}
    }
)
def put_student_by_id(id: str, student: dict, c: Redis = Depends(cache)):
    message = upsert_student(id, dict(student), c)
    if message is not None:
        return JSONResponse(status_code=status.HTTP_200_OK, content={'message': message})
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'message': 'Student ' + id + ' not found'})