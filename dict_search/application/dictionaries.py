import asyncio
from typing import List

from .datamodels import WordQueryParams, SearchResult
from .interfaces import Dictionary, SparqlTemplateService, SparqlExecutor


class RDFDictionary(Dictionary):
    def __init__(self,
                 name: str,
                 location: str,
                 available_formats: List[str],
                 sparql_template_service: SparqlTemplateService,
                 sparql_executor: SparqlExecutor):
        super().__init__(name, location, available_formats)
        self.sparql_template_service = sparql_template_service
        self.sparql_executor = sparql_executor

    async def search(self, query_params: WordQueryParams, dict_entry_type: str) -> SearchResult:
        print(f'searching in {self.name}')
        sparql_templ = self.sparql_template_service.get_filled_template(dict_entry_type, query_params)
        dict_entries = await asyncio.create_task(self.sparql_executor.execute_query(self.location, sparql_templ, dict_entry_type))
        result = SearchResult(dict_name=self.name,
                              dict_entries=dict_entries)
        return result


