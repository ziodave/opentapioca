from opentapioca.typematcher.abstracttypematcher import AbstractTypeMatcher
from opentapioca.sparqlwikidata import sparql_wikidata


class QueryTypeMatcher(AbstractTypeMatcher):

    def __init__(self, subclass_pid='P279'):
        super().__init__(subclass_pid)
        self.cache = {}

    def is_subclass(self, qid_1, qid_2):

        if qid_1 == qid_2:
            return True

        # Reply from cache if possible.
        cache_key = self.cache_key(qid_1, qid_2)
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Prepare the query.
        query = """
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>

        SELECT ( COUNT( 1 ) AS ?count ) WHERE {
            wd:%s wdt:%s* wd:%s  .
        }
        """ % (qid_1, self.subclass_pid, qid_2)

        # Run the query.
        results = sparql_wikidata(query)

        # Cache the result.
        retval = '1' == results['bindings'][0]['count']['value']
        self.cache[cache_key] = retval

        return retval

    def cache_key(self, qid_1, qid_2):
        return "%s>%s>%s" % (qid_1, self.subclass_pid, qid_2)
