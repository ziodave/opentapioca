from opentapioca.externalid.externalid import ExternalId


class ClaimExternalId(ExternalId):

    def __init__(self, claim, template):
        self.claim = claim
        self.template = template

    def get(self, item):
        # https://www.wikidata.org/wiki/Property:P214
        # https://viaf.org/viaf/144248059
        # json.claims.P214.0.mainsnak.datavalue.value => 144248059

        ids = []

        claims = item.get('claims', {})
        claim = claims.get(self.claim, [])
        for snak in claim:
            value = snak.get('mainsnak', {}).get('datavalue', {}).get('value')
            if value is not None:
                ids.append(self.template % value)

        return ids
