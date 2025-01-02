import os
import openai
from fasthtml.common import *
from starlette.responses import RedirectResponse
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from fastapi import Form
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastHTML
app = FastHTML()

# Initialize Jinja2 templates
templates = Jinja2Templates(directory='templates')

# Set up OpenAI (or 4o mini) API key from env var
openai.api_key = os.getenv("OPENAI_API_KEY")

# Optional: CORS if your site might be called from a different domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -- ROUTES --

@app.get("/")
def home(request: Request):
    """Renders the form to paste groceries."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/organize")
def organize(request: Request, groceries: str = Form(...)):
    """
    Receives the grocery list, queries the LLM, 
    returns a categorized version.
    """
    # 1) Call your LLM / OpenAI:
    prompt_text = f"Organize this grocery list into categories:\n{groceries}\n\nFormat it with headings and bullet items."
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # or your chosen model
            prompt=prompt_text,
            max_tokens=200,
            temperature=0.3,
        )
        categorized_list = response["choices"][0]["text"].strip()
    except Exception as e:
        categorized_list = f"Error calling OpenAI: {str(e)}"

    # 2) Render the same template with the result
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": categorized_list,
        }
    )
