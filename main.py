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

api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)

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
    prompt_text = (
        "Organize this grocery list into categories:\n"
        f"{groceries}\n\n"
        "Format it with headings and bullet items."
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-3.5-turbo", if "4o-mini" doesn’t exist
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_text},
            ],
        )

        categorized_list = completion.choices[0].message["content"]
    except Exception as e:
        categorized_list = f"Error calling OpenAI: {e}"

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": categorized_list,
        }
    )

serve()