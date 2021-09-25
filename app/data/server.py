from fastapi import FastAPI
from redis import Redis

app = FastAPI()


def cache():
    return Redis(host="redis", port=6379, db=0)
