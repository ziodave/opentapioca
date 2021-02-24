from json.decoder import JSONDecodeError

import requests


def sparql_wikidata(query_string, endpoint='https://query.wikidata.org/sparql'):
    headers = {
        'user-agent': 'OpenTapioca/0.1.0 (https://github.com/wetneb/opentapioca) requests/2.25.1'}
    try:
        response = requests.get(endpoint, {'query': query_string, 'format': 'json'}, headers=headers)
        results = response.json()
    except JSONDecodeError:
        print("An error occurred while running the query %s" % query_string)
        raise
    return results['results']
