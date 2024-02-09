from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="./dict_search/static"), name="static")

templates = Jinja2Templates(directory="./dict_search/templates")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, word: str = None):
    return templates.TemplateResponse(request=request, name="search.html", context={"word": word})


@app.get("/dict/{dict_name}")
async def show_dict(dict_name: str):
    return {"dict_name": dict_name, "some other info": "knvckdjfnv"}
