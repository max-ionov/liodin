import asyncio
from io import StringIO
from typing import List

from SPARQLWrapper import SPARQLWrapper, CSV
import pandas as pd

from .datamodels import DictEntry, TranslationalDictEntry
from .interfaces import SparqlExecutor


class SPARQLWrapperExecutor(SparqlExecutor):

    async def execute_query(self, location: str, sparql_query: str, dict_entry_type: str) -> List[DictEntry]:
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
            return [DictEntry(lexical_entry='there was some error')]

    def _to_bilingual(self, res) -> List[TranslationalDictEntry]:
        df = pd.read_csv(StringIO(str(res, 'utf-8')))
        dict_entries = []
        for i, gr in df.groupby(['word', 'entry_lang']):
            translations = {}
            for j, gr2 in gr.groupby('res_lang'):
                translations[j] = gr2.transl.tolist()
            if i[0] and i[1] and translations:
                entry = TranslationalDictEntry(lexical_entry=i[0], entry_lang=i[1], translations=translations)
            else:
                continue
            dict_entries.append(entry)
        return dict_entries

    def format_converter(self, res: bytes, dict_entry_type: str) -> List[DictEntry]:
        # TODO: добавить другие конвертеры для других типов словарных статей
        if dict_entry_type == 'bilingual':
            return self._to_bilingual(res)


class RDFlibExecutor(SparqlExecutor):
    ...