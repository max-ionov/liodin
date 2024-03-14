import asyncio
from io import StringIO
from typing import List, Optional

from SPARQLWrapper import SPARQLWrapper, CSV
import pandas as pd

from .datamodels import DictEntry, TranslationalDictEntry, LexicalEntry, ExplanatoryDictEntry
from .interfaces import SparqlExecutor


class SPARQLWrapperExecutor(SparqlExecutor):

    async def execute_query(self, location: str, sparql_query: str, dict_entry_type: str) -> Optional[List[DictEntry]]:
        sparql = SPARQLWrapper(location)
        sparql.setReturnFormat(CSV)
        sparql.setQuery(sparql_query)
        try:
            ret = await asyncio.create_task(asyncio.to_thread(sparql.queryAndConvert))
            return self.format_converter(ret, dict_entry_type)
        except Exception as e:
            # TODO: сделать нормальную обработку исключений желательно с возвращением сообщений об ошибках
            # здесь есть проблема с dbpedia когда запрос слишком долго делается и/или слишком много возвращает
            print(e)
            return None

    def _to_bilingual(self, res) -> List[TranslationalDictEntry]:
        df = pd.read_csv(StringIO(str(res, 'utf-8')))
        dict_entries = []
        for i, gr in df.groupby(['word', 'entry_lang']):
            translations = {}
            for j, gr2 in gr.groupby('res_lang'):
                translations[j] = gr2.transl.tolist()
            if i[0] and i[1] and translations:
                lexical_entry = LexicalEntry(text=i[0], lang=i[1])
                entry = TranslationalDictEntry(lexical_entry=lexical_entry, translations=translations)
            else:
                continue
            dict_entries.append(entry)
        return dict_entries

    def _to_explanatory(self, res) -> List[ExplanatoryDictEntry]:
        # TODO: (аня) добавить конвертер в ExplanatoryDictEntry
        ...

    def format_converter(self, res: bytes, dict_entry_type: str) -> List[DictEntry]:
        if dict_entry_type == 'bilingual':
            return self._to_bilingual(res)
        elif dict_entry_type == 'explanatory':
            return self._to_explanatory(res)


class RDFlibExecutor(SparqlExecutor):
    ...