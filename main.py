from fastapi import FastAPI, Response, status, HTTPException
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

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


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

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict['id'] = randrange(0, 100000) 
    my_posts.append(post_dict)
    return {"data": post_dict}

@app.get("/posts/latest")
def get_latest_post():
    latest_post = my_posts[len(my_posts) - 1]
    print(latest_post)
    return {"latest post": latest_post}

@app.get("/posts/{id}")
def get_posts(id: int, response: Response):

    post = find_post(id)
    if not post:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                           detail="post with id: {id} was not found")
       # response.status_code = status.HTTP_404_NOT_FOUND
       # return {"message": f"post with {id} was not found."}        
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist.")   
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# https://gurhanaras1665-8755416.postman.co/workspace/G%C3%BCrhan-Aras's-Workspace~965f9191-0a64-4e12-81e0-fb30f43a5a6b/collection/49735711-7cbf66de-211f-4900-9898-68285f80e2c4?action=share&creator=49735711
