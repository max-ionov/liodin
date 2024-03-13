from typing import Annotated, Set, List
from enum import Enum

from fastapi import FastAPI, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .application.services import DictionaryServiceImpl, DictionarySearchService, LazySparqlTemplateService
from .application.interfaces import DictionaryRepository
from .application.utils import load_dictionaries_config
from .application.datamodels import SearchParams, DictQueryParams, WordQueryParams, SearchResult


app = FastAPI()
app.mount("/static", StaticFiles(directory="./dict_search/static"), name="static")
templates = Jinja2Templates(directory="./dict_search/templates")

sparql_service = LazySparqlTemplateService('./sparql_templates.yaml')
dictionary_service = DictionaryServiceImpl(sparql_template_service=sparql_service)
dictionaries_config = load_dictionaries_config('./dictionaries.yaml')
dictionary_repo = DictionaryRepository(dictionaries_config, dict_service=dictionary_service)
search_service = DictionarySearchService(dictionary_repo)

DictName = Enum('DictName', {el.replace('-', '_'): el for el in dictionary_repo.get_all_dict_names()})


class AnnotatedSearchParams(SearchParams):
    def __init__(self,
                 w: Annotated[str, Query(description='Word or phrase to search in the dictionary')],
                 d: Annotated[Set[DictName], Query(description='Dictionaries to search in')] = None,
                 endpoints: Annotated[Set[str], Query(description='Endpoint to your own RDF dictionary')] = None,
                 entry_lang: Annotated[Set[str], Query(description='Language of lexical entry in ISO format')] = None,
                 res_lang: Annotated[Set[str], Query(description='Language of the result')] = None
                 ):
        if not d:
            if not endpoints:
                dicts = set(el.value for el in DictName)
            else:
                dicts = set()
        else:
            dicts = set(el.value for el in d)
        super().__init__(dict_info=DictQueryParams(dicts, endpoints),
                         word_info=WordQueryParams(w, entry_lang, res_lang))


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/search/")
async def api_search(search_params: Annotated[AnnotatedSearchParams, Depends(AnnotatedSearchParams)]
                     ) -> List[SearchResult]:
    return await search_service.search(search_params)


@app.get("/search", response_class=HTMLResponse, include_in_schema=False)
async def search(request: Request, search_params: Annotated[AnnotatedSearchParams, Depends(AnnotatedSearchParams)]):
    results = await search_service.search(search_params)
    # TODO: реализовать заполнение шаблонов результатами поиска
    return templates.TemplateResponse(request=request, name="search.html", context={"word": search_params.word_info.word})


@app.get("/api/dict")
async def api_dict_list():
    return dictionary_repo.get_all_dict_names()


@app.get("/dict", response_class=HTMLResponse, include_in_schema=False)
async def dict_list():
    dict_info = dictionary_repo.get_all_dict_names()  # здесь возможно мы захотим доставать еще какую-то метаинформацию, а не только названия
    # TODO: реализовать заполнение шаблонов информацией о словарях
    return


@app.get("/api/dict/{dict_name}")
async def dict(dict_name: DictName, w: str = None):
    # сделала через query, а не path, потому что тогда были бы проблемы, когда мы ищем слово "search" (пути совпали бы)
    if w:
        return {"dictionary": dict_name, "word to search": w}
    else:
        return {"dictionary": dict_name, "dictionary info": "description and wordlist"}


@app.get("/api/dict/{dict_name}/search")
async def dict_search(dict_name: DictName, w):
    return {"dictionary": dict_name, "word to search": w}
