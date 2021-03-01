from opentapioca.externalid.externalid import ExternalId


class DbpediaExternalId(ExternalId):

    def __init__(self):
        self.configs = [
            {'language': 'ar', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'bg', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'bn', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'ca', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'cj', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'cs', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'da', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'de', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'el', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'en', 'template': 'http://dbpedia.org/resource/{title}'},
            {'language': 'es', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'et', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'eu', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'fa', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'fi', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'fr', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'ga', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'gl', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'he', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'hi', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'hu', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'hy', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'ic', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'id', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'it', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'ja', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'km', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'ko', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'lo', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'lv', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'my', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'nb', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'nl', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'nn', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'no', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'pl', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'pt', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'ro', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'ru', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'sr', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'sv', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'th', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'tr', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'uk', 'template': 'http://{language}.dbpedia.org/resource/{title}'},
            {'language': 'zh', 'template': 'http://{language}.dbpedia.org/resource/{title}'}
        ]

    def get(self, item):

        ids = []

        sitelinks = item.get('sitelinks')

        for config in self.configs:
            language = config.get('language')
            template = config.get('template')
            title = sitelinks.get('{}wiki'.format(language), {}).get('title')
            if title is not None:
                ids.append(template.format(language=language, title=title))

        return ids
