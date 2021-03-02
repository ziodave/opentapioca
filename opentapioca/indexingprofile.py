import json

from opentapioca.externalid.allclaimsexternalid import AllClaimsExternalId
from opentapioca.externalid.dbpediaexternalid import DbpediaExternalId


class AliasProperty(object):
    """
    Describes how to add an additional alias based on the
    value of a property.
    """

    def __init__(self, property, prefix=None):
        self.property = property
        self.prefix = prefix

    def json(self):
        """
        JSON representation of the object
        """
        return {
            'property': self.property,
            'prefix': self.prefix,
        }

    @classmethod
    def from_json(cls, representation):
        """
        Creates an AliasProperty from its representation.
        """
        return cls(property=representation['property'],
                   prefix=representation.get('prefix'))

    def extract(self, item):
        """
        Extracts the additional aliases from an item
        :returns: a list of aliases
        """
        values = item.get_identifiers(self.property)
        if self.prefix:
            values = [self.prefix + value for value in values]
        return values


class TypeConstraint(object):
    """
    Describes a type constraint that an item should satisfy to be indexed.
    """

    def __init__(self, qid, pid):
        """
        :param qid: the qid of the target type
        :param pid: the property that the item should use to link to the type
                    (or one of its subclasses)
        """
        self.qid = qid
        self.pid = pid

    def json(self):
        """
        JSON serialization
        """
        return {
            'type': self.qid,
            'property': self.pid,
        }

    @classmethod
    def from_json(cls, representation):
        """
        Creates a TypeConstraint from its JSON representation.
        """
        return cls(qid=representation['type'], pid=representation['property'])

    def satisfied(self, item, type_matcher):
        """
        Is the type constraint satisfied for the given item?
        """
        valid_type_qids = item.get_types(self.pid)
        return any(type_matcher.is_subclass(qid, self.qid)
                   for qid in valid_type_qids)


class IndexingProfile(object):
    """
    Represents a configuration of Tapioca to index
    a particular set of elements (designated by target types
    and properties), pulling in the value of some properties
    as extra aliases, and using a particular language as default.
    """

    def __init__(self,
                 name=None,
                 solrconfig='tapioca',
                 language='en',
                 restrict_types=None,
                 restrict_properties=None,
                 alias_properties=None):
        """
        :param name: the name of the profile
        :param solrconfig: the name of the corresponding solr configset
        :param language: the language to use to select the default labels and descriptions
        :param restrict_types: include all items of any of the given types
        :param retrict_properties: also include all items bearing these Pids
        :param alias_properties: fetch the values of these properties as extra aliases
        """
        self.name = name
        self.solrconfig = solrconfig
        self.language = language
        self.restrict_types = restrict_types
        self.restrict_properties = restrict_properties
        self.alias_properties = alias_properties or []

        configs = [{'claim': 'P214', 'template': 'http://viaf.org/viaf/%s'},
                   {'claim': 'P646', 'template': 'http://g.co/kg%s'},
                   {'claim': 'P1566', 'template': 'http://sws.geonames.org/%s/'},
                   {'claim': 'P3749', 'template': 'https://maps.google.com/?cid=%s'},
                   {'claim': 'P402', 'template': 'https://www.openstreetmap.org/relation/%s'},
                   {'claim': 'P5437', 'template': 'http://eurovoc.europa.eu/%s'},
                   {'claim': 'P486', 'template': 'http://id.nlm.nih.gov/mesh/%s'},
                   {'claim': 'P2581', 'template': 'http://babelnet.org/rdf/s%s'},
                   {'claim': 'P1617', 'template': 'http://www.bbc.co.uk/things/%s#id'},
                   {'claim': 'P982', 'template': 'http://musicbrainz.org/area/%s'},
                   {'claim': 'P434', 'template': 'http://musicbrainz.org/artist/%s'},
                   {'claim': 'P435', 'template': 'http://musicbrainz.org/work/%s'},
                   {'claim': 'P435', 'template': 'http://musicbrainz.org/release-group/%s'},
                   {'claim': 'P6363', 'template': '%s'}]

        self.all_claims_external_id = AllClaimsExternalId(configs)
        self.dbpedia_external_id = DbpediaExternalId()

    def entity_to_document(self, item, type_matcher):
        """
        Given a Wikibase entity, translate it to a Solr document for indexing.
        :param type_matcher: a TypeMatcher to check subclass inclusion
        :returns: None if the entity should be skipped
        """
        valid_type_qids = item.get_types()

        # Skip if it's a Wikimedia disambiguation page.
        instance_of = item.get('claims', {}).get('P31', [])
        if instance_of:
            value = instance_of[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id')
            if value == 'Q4167410':
                print("Skipping Wikimedia disambiguation page %s" % item.get('id'))
                return

        type_features = {
            constraint.qid: constraint.satisfied(item, type_matcher)
            for constraint in self.restrict_types or []
        }
        type_features.update({
            pid: item.get_identifiers(pid) != []
            for pid in self.restrict_properties or []
        })
        correct_type = any(type_features.values())
        valid_item = correct_type or (not self.restrict_types and not self.restrict_properties)
        if not valid_item or not item.get('id').startswith('Q'):
            return

        # enlabel = item.get_default_label(self.language)
        # endesc = item.get('descriptions', {}).get(self.language, {}).get('label')
        # if not enlabel:
        #     return

        # Fetch aliases
        # aliases = item.get_all_terms()
        # aliases.remove(enlabel)

        # Edges
        edges = item.get_outgoing_edges(include_p31=False, numeric=True)

        # Extra aliases
        extra_aliases = []
        for extractor in self.alias_properties:
            extra_aliases += extractor.extract(item)

        # Stats
        nb_statements = item.get_nb_statements()
        nb_sitelinks = item.get_nb_sitelinks()

        print("Indexing %s" % item.get('id'))

        solr_doc = {
            'id': item.get('id'),
            'revid': item.get('lastrevid') or 1,
            # 'label': enlabel,
            # 'desc': endesc or '',
            'edges': edges,
            # 'types': json.dumps(type_features),
            # 'aliases': list(aliases),
            # 'extra_aliases': extra_aliases,
            'nb_statements': nb_statements,
            'nb_sitelinks': nb_sitelinks,
            'types': json.dumps(type_features),
        }

        for label in item.get('labels', {}).values():
            language = label.get('language')
            if self.is_language_supported(language):
                solr_doc[f"tag_{language}_name"] = label.get('value')

                solr_doc[f"tag_{language}_alias"] = [label.get('value')]
                for alias in item.get('aliases', {}).get(language, []):
                    solr_doc[f"tag_{language}_alias"].append(alias.get('value'))

        for description in item.get('descriptions', {}).values():
            if self.is_language_supported(description.get('language')):
                solr_doc[f"description_{description.get('language')}"] = description.get('value')

        solr_doc['same_as_ss'] = self.dbpedia_external_id.get(item) + self.all_claims_external_id.get(item)

        # Add geo coordinates.
        p625 = item.get('claims', {}).get('P625', [])
        if p625:
            value = p625[0].get('mainsnak', {}).get('datavalue', {}).get('value', {})
            lat = value.get('latitude')
            lng = value.get('longitude')
            if lat is not None and lng is not None:
                solr_doc['latitude_d'] = lat
                solr_doc['longitude_d'] = lng

        # Add start date.
        p580 = item.get('claims', {}).get('P580', [])
        if p580:
            value = p580[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('time')
            if value is not None:
                solr_doc['start_time_dt'] = value

        # Add end date.
        p582 = item.get('claims', {}).get('P582', [])
        if p582:
            value = p582[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('time')
            if value is not None:
                solr_doc['end_time_dt'] = value

        return solr_doc

    @classmethod
    def load(cls, filename):
        """
        Loads an indexing profile from a JSON file.
        """
        with open(filename, 'r') as f:
            repr = json.load(f)
            extractors = [
                AliasProperty.from_json(definition)
                for definition in repr.get('alias_properties') or []
            ]
            types = [
                TypeConstraint.from_json(definition)
                for definition in repr.get('restrict_types') or []
            ]
            return cls(
                solrconfig=repr.get('solrconfig'),
                language=repr.get('language'),
                name=repr.get('name'),
                restrict_types=types,
                restrict_properties=repr.get('restrict_properties'),
                alias_properties=extractors)

    def save(self, filename):
        """
        Saves an indexing profile to a file, in JSON.
        """
        with open(filename, 'w') as f:
            json.dump(self.json(), f, indent=4)

    def json(self):
        """
        Returns a dict representation of the profile
        """
        return {
            'name': self.name,
            'solrconfig': self.solrconfig,
            'language': self.language,
            'restrict_types': [
                constraint.json() for constraint in self.restrict_types
            ],
            'restrict_properties': self.restrict_properties,
            'alias_properties': [
                extractor.json() for extractor in self.alias_properties
            ],
        }

    @staticmethod
    def is_language_supported(param):
        return param in [
            'ar',
            'bg',
            'bn',
            'ca',
            'cj',
            'cs',
            'da',
            'de',
            'el',
            'en',
            'es',
            'et',
            'eu',
            'fa',
            'fi',
            'fr',
            'ga',
            'gl',
            'he',
            'hi',
            'hu',
            'hy',
            'ic',
            'id',
            'it',
            'ja',
            'km',
            'ko',
            'lo',
            'lv',
            'my',
            'nb',
            'nl',
            'nn',
            'no',
            'pl',
            'pt',
            'ro',
            'ru',
            'sr',
            'sv',
            'th',
            'tr',
            'uk',
            'zh'
        ]
