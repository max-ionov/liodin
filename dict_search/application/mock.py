from .datamodels import SearchResult, LexicalEntry, TranslationalDictEntry, WordQueryParams
from .interfaces import SparqlTemplateService


mock_results = [
        SearchResult(
            dict_name='acoli-dict',
            dict_entries=[
                TranslationalDictEntry(
                    lexical_entry=LexicalEntry(text='cat', lang='en'),
                    translations={
                        'es': ['gato'],
                        'gl': ['gato', 'micho', 'mico'],
                        'kk': ['мысық']
                    }
                )
            ]
        ),
        SearchResult(
            dict_name='https://kaiko.getalp.org/sparql',
            dict_entries=[
                TranslationalDictEntry(
                    lexical_entry=LexicalEntry(text='cat', lang='en'),
                    translations={
                        'aa': ['dummuutá'],
                        'ab': ['ацгә'],
                        'abs': ['pus', 'tusa'],
                        'ace': ['mië'],
                        'acm': ['بزونة'],
                        'acw': ['بسة', 'عُرِّي'],
                        'ady': ['кӏэтыу']
                    }
                )
            ]
        )
    ]


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
