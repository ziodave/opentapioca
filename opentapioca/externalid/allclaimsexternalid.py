from opentapioca.externalid.claimexternalid import ClaimExternalId
from opentapioca.externalid.externalid import ExternalId


class AllClaimsExternalId(ExternalId):

    def __init__(self, configs):
        self.claims = []
        for config in configs:
            self.claims.append(ClaimExternalId(config.get('claim'), config.get('template')))

    def get(self, item):
        ids = []

        for claim in self.claims:
            ids += claim.get(item)

        return ids
