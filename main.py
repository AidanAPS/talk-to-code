from dotenv import load_dotenv
from gitingest import ingest
from google import genai
import os, git

def clone_repo(repo_url: str, repo_dir: str) -> None:
    """Clones the repository if not already cloned."""
    if os.path.exists(repo_dir):
        return
    os.makedirs(repo_dir, exist_ok=True)
    git.Repo.clone_from(repo_url, repo_dir, depth=2)

def generate_response(question, tree, content, client):
    """Generates a response from Gemini AI for the given question."""
    system_instruction = "You are a coding expert. Your mission is to answer all code-related questions with given context and instructions."
    
    contents = [
        """
        Context:
        - The entire codebase is provided below.
        - This is a JavaScript application written in Electron
        - The backend is Firestore
        - Here is the directory tree of all of the files in the codebase:
        """,
        tree,
        """
        - Then each of the files are concatenated together. You will find all of the code you need:
        """,
        content,
    ]

    full_prompt = system_instruction + "\n" + "\n".join(contents) + "\n" + question

    response = client.models.generate_content(model="gemini-2.0-flash", contents=full_prompt)

    with open("./output.md", "w") as file:
        file.write(response.text)
    
    print("Response saved to output.md!")
    print(response.usage_metadata)

def interactive_mode(client, tree, content):
    """Continuously asks for questions until 'q' is entered."""
    print("Enter your questions (type 'q' to quit):")
    while True:
        question = input("\nQuestion: ")
        
        if question.lower() == 'q':
            print("Exiting program.")
            break
            
        generate_response(question, tree, content, client)

# Load environment variables
load_dotenv()

# Retrieve repo and API key
repo_url = os.getenv('GITHUB_REPO')
repo_dir = "./repo"
api_key = os.getenv('GEMINI_API_KEY')

# Ensure API key is loaded
if not api_key:
    raise ValueError("Error: GEMINI_API_KEY is not loaded. Check your .env file.")

# Clone the repository
clone_repo(repo_url, repo_dir)

# Ingest the repository
exclude_patterns = ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.ico", "*.webp", ".git/", "*.gitkeep"]
_, tree, content = ingest(repo_dir, exclude_patterns=set(exclude_patterns))

# Configure Gemini AI client
client = genai.Client(api_key=api_key)

# Start interactive mode
interactive_mode(client, tree, content)
