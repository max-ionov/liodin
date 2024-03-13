from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set, Union
from pydantic import BaseModel


# user query application
@dataclass
class WordQueryParams:
    word: str
    entry_lang: Optional[Set[str]] = None
    result_lang: Optional[Set[str]] = None


@dataclass
class DictQueryParams:
    dicts: Optional[Set[str]] = None
    endpoints: Optional[Set[str]] = None


@dataclass
class DictConfig:
    name: str
    format_: str
    location: str
    available_formats: Optional[List[str]] = field(default_factory=list)


# search results application
@dataclass
class SearchParams:
    dict_info: DictQueryParams
    word_info: WordQueryParams


class LexicalEntry(BaseModel):
    text: str
    lang: str


class DictEntry(BaseModel):
    lexical_entry: LexicalEntry


# here should be pydantic application inherited from DictEntry for different dictionary types - explanatory, bilingual etc.
# TODO: добавить другие типы словарных статей и (возможно) поменять структуру словарной статьи переводного словаря
class TranslationalDictEntry(DictEntry):
    translations: Dict[str, List[str]]


# TODO: возможно добавить инфу, что если что-то пошло не так?
class SearchResult(BaseModel):
    dict_name: str
    dict_entries: List[Union[DictEntry, TranslationalDictEntry]]