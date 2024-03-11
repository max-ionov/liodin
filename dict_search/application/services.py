import asyncio
from dataclasses import asdict
from typing import Optional, List

import yaml

from .datamodels import WordQueryParams, DictConfig, SearchParams, SearchResult, DictQueryParams
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


class MockSparqlTemplateService(SparqlTemplateService):
    def get_filled_template(self, template_name: str, query_params: WordQueryParams) -> str:
        return """PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
PREFIX vartrans: <http://www.w3.org/ns/lemon/vartrans#>
PREFIX decomp: <http://www.w3.org/ns/lemon/decomp#>
PREFIX lexinfo: <http://www.lexinfo.net/ontology/2.0/lexinfo#>
PREFIX dbnary: <http://kaiko.getalp.org/dbnary#>

SELECT ?word ?transl (LANG(?word) AS ?entry_lang) (LANG(?transl) AS ?res_lang)
WHERE {  
  GRAPH ?g {
    ?entry1 a ontolex:LexicalEntry ;
            (ontolex:lexicalForm|ontolex:canonicalForm|ontolex:otherForm)/ontolex:writtenRep ?word .
    ?sense1 ontolex:isSenseOf|^ontolex:sense ?entry1 .
    
    OPTIONAL {
      ?tr vartrans:source ?sense1 ;
          vartrans:target ?sense2 .
      
      ?sense2 ontolex:isSenseOf|^ontolex:sense ?entry2 .
      ?entry2 a ontolex:LexicalEntry ;
              (ontolex:lexicalForm|ontolex:canonicalForm|ontolex:otherForm)/ontolex:writtenRep ?transl .
    }
    
    OPTIONAL {
      ?tr2 dbnary:isTranslationOf ?sense1 ;
         dbnary:writtenForm ?transl .
    }
    
    FILTER(?word = "cat"@en)
    #FILTER(STR(?word1) = "cat")
    #FILTER(REGEX(STR(?word1), "^cat.*$"))
    #FILTER(REGEX(STR(?word1), "^cat.*$") && LANG(?word1) = "en")
    #FILTER(REGEX(STR(?word1), "^cat.*$") && LANG(?word2) = "es")
    #FILTER(LANG(?word1) = "en")
  }
} LIMIT 100
"""


class LazySparqlTemplateService(SparqlTemplateService):
    # TODO: нормально реализовать работу со спаркл шаблонами - придумать как хранить/заполнять
    def __init__(self, templates_path: str):
        with open(templates_path, 'r') as f:
            self.templates = yaml.safe_load(f)

    def get_filled_template(self, template_name: str, query_params: WordQueryParams) -> str:
        template = self.get_template(template_name)
        return self.fill_template(template, query_params)

    def get_template(self, template_name: str) -> dict:
        return self.templates[template_name]

    def fill_template(self, template: dict, query_params: WordQueryParams) -> str:
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
