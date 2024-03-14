import asyncio
from dataclasses import asdict
from typing import Optional, List

import yaml

from .datamodels import WordQueryParams, DictConfig, SearchParams, SearchResult
from .interfaces import DictionaryService, Dictionary, SparqlTemplateService, DictionaryRepository
from .sparql_executor import SPARQLWrapperExecutor, RDFlibExecutor
from .dictionaries import RDFDictionary


class DictionaryServiceImpl(DictionaryService):
    def __init__(self, sparql_template_service: SparqlTemplateService):
        self.sparql_template_service = sparql_template_service

    def create_dictionary(self, config: DictConfig) -> Optional[Dictionary]:
        if config.format_ == 'rdf':
            if config.location.startswith('http'):
                sparql_executor = SPARQLWrapperExecutor()
            else:
                sparql_executor = RDFlibExecutor()

            available_formats = self.define_dict_entry_format(config)

            return RDFDictionary(
                name=config.name,
                location=config.location,
                available_formats=available_formats,
                sparql_template_service=self.sparql_template_service,
                sparql_executor=sparql_executor
            )
        else:
            raise ValueError('Unknown dictionary format')

    def define_dict_entry_format(self, config: DictConfig) -> List[str]:
        # TODO: реализовать определения типа словарной статьи, которую можно извлекать из словаря
        if config.available_formats:
            return config.available_formats
        return ['bilingual']


class DictionarySearchService:
    def __init__(self, dictionary_repo: DictionaryRepository):
        self.dictionary_repo = dictionary_repo

    def create_search_tasks(self, search_params: SearchParams) -> List[asyncio.Task]:
        tasks = []
        # Search in pre-defined dictionaries
        for name in search_params.dict_info.dicts:
            dictionary = self.dictionary_repo.find_dictionary_by_name(name)
            if dictionary:
                dict_entry_type = dictionary.available_formats[0]
                tasks.append(asyncio.create_task(dictionary.search(search_params.word_info, dict_entry_type)))

        # Search in user-provided dictionaries
        if search_params.dict_info.endpoints:
            for endpoint in search_params.dict_info.endpoints:
                user_dict_config = DictConfig(name=endpoint, format_='rdf', location=endpoint)
                user_dict = self.dictionary_repo.dict_service.create_dictionary(user_dict_config)
                if user_dict:
                    dict_entry_type = user_dict.available_formats[0]
                    tasks.append(asyncio.create_task(user_dict.search(search_params.word_info, dict_entry_type)))
        return tasks

    async def search(self, search_params: SearchParams) -> List[SearchResult]:
        search_tasks = self.create_search_tasks(search_params)
        results = await asyncio.gather(*search_tasks)
        return results


class LazySparqlTemplateService(SparqlTemplateService):
    # TODO: нормально реализовать работу со спаркл шаблонами - придумать как хранить/заполнять
    def __init__(self, templates_path: str):
        with open(templates_path, 'r') as f:
            self.templates = yaml.safe_load(f)

    def get_filled_template(self, template_name: str, query_params: WordQueryParams) -> str:
        template = self.get_template(template_name)
        if template_name == 'bilingual':
            return self.fill_bilingual_template(template, query_params)
        elif template_name == 'explanatory':
            # TODO: (аня) написать заполнение шаблона для запроса к толковому словарю
            ...

    def get_template(self, template_name: str) -> dict:
        return self.templates[template_name]

    def fill_bilingual_template(self, template: dict, query_params: WordQueryParams) -> str:
        query = asdict(query_params)
        params = {p: v for p, v in query.items() if v}
        if 'entry_lang' in params:
            params['entry_lang'] = [el for el in params['entry_lang']][0]
            if 'result_lang' in params:
                params['result_lang'] = [el for el in params['result_lang']][0]
                ch = 3
            else:
                ch = 1
        else:
            if 'result_lang' in params:
                params['result_lang'] = [el for el in params['result_lang']][0]
                ch = 2
            else:
                ch = 0
        return template['body'].format(filter=template['filters'][ch].format(**params))
