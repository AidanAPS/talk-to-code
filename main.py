from dotenv import load_dotenv
from gitingest import ingest
from google import genai
import os, git

QUESTION = "Can you summarize this codebase and locate the core files"

load_dotenv()

repo_url = os.getenv('GITHUB_REPO')
repo_dir = "./repo"

def clone_repo(repo_url: str, repo_dir: str) -> None:
    if os.path.exists(repo_dir):
        return
    os.makedirs(repo_dir, exist_ok=True)
    git.Repo.clone_from(repo_url, repo_dir, depth=2)

clone_repo(repo_url, repo_dir)
exclude_patterns = ["*.png","*.jpg","*.jpeg","*.gif","*.svg","*.ico","*.webp",".git/","*.gitkeep",]
_, tree, content = ingest(repo_dir, exclude_patterns=set(exclude_patterns))
     
system_instruction = "You are a coding expert. Your mission is to answer all code related questions with given context and instructions."
contents = [
    """
    Context:
    - The entire codebase is provided below.
    - This is a JavaScript application written in Electron
    - The backend is Firestore
    - Here is directory tree of all of the files in the codebase:
    """,
    tree,
    """
    - Then each of the files are concatenated together. You will find all of the code you need:
    """,
    content,
]

contents = system_instruction + "\n" + "\n".join(contents) + "\n" + QUESTION
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

response = client.models.generate_content(model="gemini-2.0-flash", contents=contents)

with open("./output.md", "w") as file:
    file.write(response.text)
print(response.usage_metadata)