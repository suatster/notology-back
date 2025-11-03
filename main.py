from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional

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

@app.post("/createposts")
def create_posts(new_post: Post):
    print(new_post)
    print(new_post.dict())
    print(new_post.title)
    print(new_post.content)
    print(new_post.published)
    print(new_post.rating)
    return {"data": new_post}
