from enum import Enum
from typing import List, Annotated, Union

from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="./dict_search/static"), name="static")

templates = Jinja2Templates(directory="./dict_search/templates")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


class DictName(str, Enum):
    # можно для словарей задать Enum, чтобы валидировать
    laz = "laz"
    georgian = "georgian"


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, w: str = None, d: Annotated[Union[List[DictName], None], Query()] = None):
    # в d можно будет передавать список словарей, по которым будет происходить поиск, или не передавать ничего
    # тогда будет искаться по всему, что есть
    return templates.TemplateResponse(request=request, name="search.html", context={"word": w})


@app.get("/dict")
async def dict_list():
    return {"dicts": ["dict1", "dict2", "dict3"]}


@app.get("/dict/{dict_name}")
async def dict(dict_name: DictName, w: str = None):
    # сделала через query, а не path, потому что тогда были бы проблемы, когда мы ищем слово "search" (пути совпали бы)
    if w:
        return {"dictionary": dict_name, "word to search": w}
    else:
        return {"dictionary": dict_name, "dictionary info": "description and wordlist"}


@app.get("/dict/{dict_name}/search")
async def dict_search(dict_name: DictName, w):
    return {"dictionary": dict_name, "word to search": w}
