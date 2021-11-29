from typing import Optional
from fastapi import FastAPI
from app.bibformat import *

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.get("/validate/{kthid}")
def read_validate(kthid: str):
    return {"result": fix_kthid(kthid, idtype="person")}
