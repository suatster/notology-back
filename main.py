from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True 
    rating: Optional[int] = None

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1}, {"title": "favourite foods", "content": "I like pizza", "id": 2}]

@app.get("/hello/world")
async def root():
    return {"message": "Hello World!"} 


@app.get("/welcome")
async def root():
    return {"message": "Welcome to my API."} 

@app.get("/posts")
def get_posts():
    return {"data": my_posts}

# @app.post("/createposts")
# def create_posts(payload: dict = Body(...)):
   # print(payload)
   # print(payload["title"]) 
   # print(payload["content"]) 
   # return {"new_post": f"title {payload["title"]} content {payload["content"]}" } 

@app.post("/posts")
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict['id'] = randrange(0, 100000) 
    my_posts.append(post_dict)
    return {"data": post_dict}
