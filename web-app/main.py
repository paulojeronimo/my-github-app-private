from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import requests
import os

app = FastAPI()

class RepositoryData(BaseModel):
    repository_name: str

def create_repository(repository_name: str, github_token: str):
    url = 'https://api.github.com/user/repos'
    headers = {'Authorization': f'token {github_token}'}
    data = {'name': repository_name, 'private': True}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        return response.json()['ssh_url']
    else:
        raise HTTPException(status_code=response.status_code, detail=f"Error creating repository: {response.text}")

def add_user_as_collaborator(username: str, repository_name: str, github_token: str):
    url = f'https://api.github.com/repos/{username}/{repository_name}/collaborators/{username}'
    headers = {'Authorization': f'token {github_token}'}

    response = requests.put(url, headers=headers)

    if response.status_code == 204:
        return {"message": f"User {username} added as collaborator successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=f"Error adding user as collaborator: {response.text}")

def get_github_token():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise HTTPException(status_code=401, detail="GitHub token not provided")
    return token

@app.post("/create_repository/{username}")
async def create_repository_and_add_user(username: str, repository_data: RepositoryData, github_token: str = Depends(get_github_token)):
    try:
        repository_url = create_repository(repository_data.repository_name, github_token)
        response = add_user_as_collaborator(username, repository_data.repository_name, github_token)
        return {"repository_url": repository_url, **response}
    except HTTPException as e:
        raise e
