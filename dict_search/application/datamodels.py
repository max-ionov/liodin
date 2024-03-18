from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set, Union
from pydantic import BaseModel


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
    about: str
    available_formats: Optional[List[str]] = field(default_factory=list)



@dataclass
class SearchParams:
    dict_info: DictQueryParams
    word_info: WordQueryParams


class LexicalEntry(BaseModel):
    text: str
    lang: str


class DictEntry(BaseModel):
    lexical_entry: LexicalEntry


class TranslationalDictEntry(DictEntry):  # тк наследуется от DictEntry имеет все его поля
    translations: Dict[str, List[str]]  # {язык перевода: [перевод1, перевод2, ...]


class ExplanatoryDictEntry(DictEntry):
    # TODO: (аня) добавить структуру словарной статьи
    ...


class SearchResult(BaseModel):
    dict_name: str  # название словаря
    dict_entries: Optional[List[Union[
        DictEntry,
        TranslationalDictEntry,
        ExplanatoryDictEntry
    ]]]  # [словарнаяСтатья1, словарнаяСтатья2, ...]
