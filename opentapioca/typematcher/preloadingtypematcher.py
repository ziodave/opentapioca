import logging
from collections import Set

from opentapioca.typematcher.abstracttypematcher import AbstractTypeMatcher
from opentapioca.sparqlwikidata import sparql_wikidata
from opentapioca.utils import to_q

logger = logging.getLogger(__name__)


class PreloadingTypeMatcher(AbstractTypeMatcher):

    def __init__(self, subclass_pid='P279'):
        super().__init__(subclass_pid)
        self.cache = {}

    def is_subclass(self, qid_1, qid_2):

        # Check if qid_1 is child of qid_2.
        return self.in_qid(qid_1, qid_2, set())

    def in_qid(self, subclass_qid, superclass_qid, been_there):

        # Protect from circular loops.
        if subclass_qid in been_there:
            return False
        else:
            been_there.add(subclass_qid)

        # Cache the subclass data.
        self.build_cache(subclass_qid)

        #  Identity                       or parent found
        if subclass_qid == superclass_qid or superclass_qid in self.cache[subclass_qid]:
            return True
        else:
            for parent_qid in self.cache[subclass_qid]:
                if self.in_qid(parent_qid, superclass_qid, been_there):
                    return True

        return False

    def build_cache(self, subclass_qid):

        # Stop building the cache if we reached the needle.
        if subclass_qid in self.cache.keys():
            return

        # Set the initial set.
        self.cache[subclass_qid] = set()

        # Prepare the query.
        query = """
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>

        SELECT ?parent WHERE {
            wd:%s wdt:%s ?parent  .
        }
        """ % (subclass_qid, self.subclass_pid)

        # Run the query.
        results = sparql_wikidata(query)

        for result in results["bindings"]:
            q = to_q(result["parent"]["value"])
            self.cache[subclass_qid].add(q)
