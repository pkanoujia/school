from fastapi import Path
from sqlalchemy import Boolean
from sqlalchemy.orm import Session
from typing_extensions import Annotated
from starlette import status
from fastapi import FastAPI,Depends, HTTPException
import model
from database import engine, sessionLocal
from model import Todos
from pydantic import BaseModel, Field
app =FastAPI()



model.Base.metadata.create_all(bind =engine)

class TodoRequest(BaseModel):
    title:str = Field(min_length=3)
    description:str =Field(min_length=3,max_length=100)
    priority:int = Field(gt=0,lt=6)
    complete:bool

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session,Depends(get_db)]

@app.get("/")
def read_all(db:db_dependency):
    return db.query(Todos).all()

@app.get("/path/{todos_id}",status_code = status.HTTP_200_OK)
def read_by_ids(db:db_dependency,todos_id:int = Path(gt=0)):
    todos_model = db.query(Todos).filter(Todos.id == todos_id).first()
    if todos_model is not None:
        return todos_model
    raise HTTPException(status_code=404,detail="to do not found")

@app.post("/update",status_code=status.HTTP_201_CREATED)
def create_record(db:db_dependency,todorequest:TodoRequest):
    todo_model = Todos(**todorequest.model_dump())
    db.add(todo_model)
    db.commit()

@app.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
def update_todo(db:db_dependency,todo_id:int,Todorequest:TodoRequest):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise  HTTPException(status_code=404,detail="to do not found") 
    todo_model.title = Todorequest.title
    todo_model.description = Todorequest.description
    todo_model.priority = Todorequest.priority
    todo_model.complete = Todorequest.complete

    db.add(todo_model)
    db.commit()


@app.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
def deleteRecord(db:db_dependency,todo_id:int):
    todo_model =db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()


 


        