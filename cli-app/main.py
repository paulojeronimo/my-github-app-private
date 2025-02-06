import requests
import argparse
import os

def create_repository(username: str, repository_name: str):
    url = f'http://127.0.0.1:8000/create_repository/{username}'
    headers = {'Content-Type': 'application/json'}
    data = {'repository_name': repository_name}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise RuntimeError(f"Error creating repository: {response.status_code} - {response.text}")

def main():
    parser = argparse.ArgumentParser(description="Creates a private repository on GitHub for the specified user.")
    parser.add_argument("username", help="The GitHub username.")
    parser.add_argument("repository_name", help="The name of the repository to be created.")

    args = parser.parse_args()

    username = args.username
    repository_name = args.repository_name

    try:
        result = create_repository(username, repository_name)
        print("Repository created successfully:")
        print(f"URL: {result['repository_url']}")
        print(f"Message: {result['message']}")

    except RuntimeError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
