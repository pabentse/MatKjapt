import os
from openai import OpenAI
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

os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key='OPENAI_API_KEY')

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
    #use 4o mini to generate the categories
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_text},
        ],
    )

    # 2) Parse the result
    categorized_list = completion.choices[0].message['content']


    # 3) Render the same template with the result
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": categorized_list,
        }
    )

# -- MAIN --
serve()