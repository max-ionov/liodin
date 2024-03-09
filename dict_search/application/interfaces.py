from abc import ABC, abstractmethod
from typing import List, Optional, Dict

from .datamodels import WordQueryParams, DictEntry, DictConfig, SearchResult


class SparqlTemplateService(ABC):
    @abstractmethod
    def get_filled_template(self, template_name: str, query_params: WordQueryParams) -> str:
        pass


class SparqlExecutor(ABC):
    @abstractmethod
    async def execute_query(self, location: str, sparql_query: str, dict_entry_type: str) -> List[DictEntry]:
        pass


class Dictionary(ABC):
    def __init__(self, name: str, location: str, available_formats: List[str]):
        self.name = name
        self.location = location
        self.available_formats = available_formats  # for ex: translational, explanatory, etc

    @abstractmethod
    async def search(self, query_params: WordQueryParams, dict_entry_type: str) -> SearchResult:
        pass


class DictionaryService(ABC):
    @abstractmethod
    def create_dictionary(self, config: DictConfig) -> Optional[Dictionary]:
        ...


class DictionaryRepository:
    def __init__(self, dictionaries_config: List[DictConfig], dict_service: DictionaryService):
        self.dict_service = dict_service
        self.dictionaries = self.init_dicts_from_config(dictionaries_config)

    def init_dicts_from_config(self, dictionaries_config: List[DictConfig]) -> Dict[str, Dictionary]:
        dictionaries = {}
        for entry in dictionaries_config:
            dictionaries[entry.name] = self.dict_service.create_dictionary(entry)
        return dictionaries

    def find_dictionary_by_name(self, name: str) -> Optional[Dictionary]:
        return self.dictionaries.get(name)

    def get_all_dict_names(self):
        return list(self.dictionaries.keys())