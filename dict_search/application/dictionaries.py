from typing import List

from .datamodels import WordQueryParams, DictEntry
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

    def search(self, query_params: WordQueryParams, dict_entry_type: str) -> List[DictEntry]:
        sparql_templ = self.sparql_template_service.get_filled_template(dict_entry_type, query_params)
        return self.sparql_executor.execute_query(self.location, sparql_templ, dict_entry_type)


