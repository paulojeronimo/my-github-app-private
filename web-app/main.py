from fastapi import FastAPI, HTTPException
import requests
import os
import tempfile
import uvicorn
import git

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPOSITORY_OWNER = os.environ.get("REPOSITORY_OWNER")
ACCESSMENT_NAME = 'accessment-123'

def read_and_replace_template(template_path: str, replacements: dict) -> str:
    try:
        with open(template_path, 'r') as file:
            content = file.read()
            for key, value in replacements.items():
                content = content.replace(key, value)
            return content
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail=f"Template file not found at {template_path}"
        )


def create_repository(repository_name: str, username: str):
    url = 'https://api.github.com/user/repos'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    data = {'name': repository_name, 'private': True}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        ssh_url = response.json()['ssh_url']
        template_path = os.path.join('templates', 'README.adoc')
        readme_content = read_and_replace_template(
            template_path,
            {
                '${repository_owner}': REPOSITORY_OWNER,
                '${repository_name}': repository_name,
                '${username}': username,
            }
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = git.Repo.clone_from(ssh_url, temp_dir)
            readme_path = os.path.join(temp_dir, 'README.adoc')
            with open(readme_path, 'w') as f:
                f.write(readme_content)
            repo.index.add(['README.adoc'])
            repo.index.commit('Initial commit with README.adoc')
            repo.remote().push()
        return ssh_url
    else:
        raise HTTPException(status_code=response.status_code, detail=f"Error creating repository: {response.text}")


def add_user_as_collaborator(username: str, repository_name: str):
    url = f'https://api.github.com/repos/{REPOSITORY_OWNER}/{repository_name}/collaborators/{username}'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.put(url, headers=headers)
    if response.status_code in (201, 204):
        return {"message": f"User {username} successfully added as collaborator."}
    else:
        raise HTTPException(status_code=response.status_code, detail=f"Error {response.status_code} adding user as collaborator: {response.text}")


app = FastAPI()


@app.post("/create_repository/{username}")
async def create_repository_and_add_user(username: str):
    try:
        if not GITHUB_TOKEN:
            raise HTTPException(status_code=401, detail="GitHub token not provided")
        if not REPOSITORY_OWNER:
            raise HTTPException(status_code=401, detail="Repository owner not provided")
        repository_name = f'{ACCESSMENT_NAME}-{username}'
        repository_url = create_repository(repository_name, username)
        response = add_user_as_collaborator(username, repository_name)
        return {"repository_url": repository_url, **response}
    except HTTPException as e:
        raise e


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
