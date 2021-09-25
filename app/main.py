from model.student import *
from model.log import Message
from biz.db import *
from data.server import *

from fastapi import Depends, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from typing import Optional

# GET methods
@app.get('/')
def read_root(c: Redis = Depends(cache)):
    if len(get_all_students(c)) == 0:
        return 'Students list is empty, please add new students'
    return get_list_all_students(c)

@app.get('/students/sort/{sortBy}')
def get_students_by_sortparam(sortBy: Optional[str] = None, c: Redis = Depends(cache)):
    val = 0
    if sortBy == 'id':
        return sorted(get_list_all_students(c), key=lambda d: int(d['id']))
    elif sortBy == 'name':
        return sorted(get_list_all_students(c), key=lambda d: str(d['name']))
    elif sortBy == 'gpa':
        student_list = filter(lambda d: d['gpa'] != None, get_list_all_students(c))
        return sorted(student_list, key=lambda d: float(d['gpa']) and d['gpa'] != None)
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'message': 'Student list not found'})


@app.get(
    'students/find/{student_id}',
    responses={
        200: {
            'content': Student,
            'description': 'Return student details'
        },
        404: {'model': Message}
    }
)
async def find_student(student_id: str, c: Redis = Depends(cache)):
    print(student_id)
    if get_student_by_id(student_id, c) is not None:
        return JSONResponse(status_code=status.HTTP_200_OK, content=get_student_by_id(student_id, c))
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'message': 'Student detail not found'})


# POST methods
@app.post('/student/postsingle')
def create_student(student: Student, c: Redis = Depends(cache)):
    insert_student(jsonable_encoder(student), c)
    return student.name + ' credentials created'

@app.post('/student/postmultiple')
def create_students(students: List[Student], c: Redis = Depends(cache)):
    response = []
    for s in students:
        insert_student(jsonable_encoder(s), c)
        response.append(s.name + ' credentials created')
    return JSONResponse(status_code=status.HTTP_200_OK, content={'message': '; '.join(response)})

@app.post(
    '/deleteall',
    responses={
        200: {
            'content': list,
            'description': 'Return student list'
        },
        404: {'model': Message}
    }
)
def delete_all(c: Redis = Depends(cache)):
    if delete_all_students(c):
        return JSONResponse(status_code=status.HTTP_200_OK, content={'message': 'Students list is cleared'})
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={'message': 'Interal Server Error'})