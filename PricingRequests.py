import requests


# base chaos
def convertCurrency(seller):
    value = 0
    divRatio = 1/250
    if seller['currency'] == 'divine':
        value = seller['amount'] / divRatio
    else:
        value = seller['amount']

    return value


def RequestGemJson(gem, POESESSID, league):
    # phantasmal
    if gem['type'] == 'Alternate3':
        typeName = '3'
    # divergent
    if gem['type'] == 'Alternate2':
        typeName = '2'
    # anomalous
    if gem['type'] == 'Alternate1':
        typeName = '1'
    if gem['type'] == 'Default':
        typeName = '0'

    if gem['support']:
        gem['name'] = gem['name'] + ' Support'

    query = '{"query":{"status":{"option":"online"},"type":"' + gem['name'] \
            + '","stats":[{"type":"and","filters":[]}],"filters":{"misc_filters":{"filters":{"gem_alternate_quality":{"option":"' \
            + typeName + '"},"gem_level":{"min":' + gem['level'] + '},"quality":{"min":' \
            + gem['quality'] + '}}}}},"sort":{"price":"asc"}}'

    r = requests.post("https://www.pathofexile.com/api/trade/search/" + league,
                      data=query,
                      headers={"User-Agent": POESESSID,
                               "Content-Type": "application/json",
                               "Accept": "application/json"})

    if r.status_code != 200:
        print('------------')
        print(query)
        print(r.status_code)
        print(r.json())
        print('------------')

    response = r.json()
    headers = r.headers
    limits = headers['X-Rate-Limit-Ip']
    limits = limits.split(',')
    limits = limits[-1].split(':')

    delay = int(limits[1]) / int(limits[0])

    return response, delay, r.status_code


# {"query":{"status": {"option": "online"},"name": "Apep's Rage","stats": [{"type": "and","filters": []}]},"sort": {"price": "asc"}}
# {
#   "type": "and",
#   "filters": [
#     {
#       "id": "explicit.stat_388617051",
#       "disabled": true
#     },
#     {
#       "id": "explicit.stat_299054775",
#       "disabled": true,
#       "value": {
#         "min": 55
#       }
#     },
#     {
#       "id": "explicit.stat_1256719186",
#       "disabled": true,
#       "value": {
#         "min": 36
#       }
#     }

def requestUniqueJson(item, modId, modValue, POESESSID, league):
    item['name'] = item['name'].replace('\\', '')

    filters = ''
    for idx, mods in enumerate(modId):
        if mods != 'Not Found':
            if modValue[idx]:
                filters += '{"id": "' + mods[0] + '","value": {"min": ' + str(modValue[idx][0]) + '}},'
            else:
                filters += '{"id": "' + mods[0] + '"},'

    filters = filters[:-1]

    query = '{"query":{"status":{"option":"online"},"name":"' + item['name'] + '"' \
            + ',"stats":[{"type":"and","filters":[' \
            + filters \
            + ']}]},"sort":{"price":"asc"}}'

    r = requests.post("https://www.pathofexile.com/api/trade/search/" + league,
                      data=query,
                      headers={"User-Agent": POESESSID,
                               "Content-Type": "application/json",
                               "Accept": "application/json"})

    if r.status_code != 200:
        print('------------')
        print(query)
        print(r.status_code)
        print(r.json())
        print('------------')

    response = r.json()
    headers = r.headers
    limits = headers['X-Rate-Limit-Ip']
    limits = limits.split(',')
    limits = limits[-1].split(':')

    delay = int(limits[1]) / int(limits[0])

    return response, delay, r.status_code


def RequestPriceData(jsonResponse, POESESSID):
    url = 'https://www.pathofexile.com/api/trade/fetch/'
    # build query
    items = ''
    for idx, i in enumerate(jsonResponse['result']):
        if idx < 10:
            items = items + i + ','
    # remove last ','
    items = items[:-1]
    query = items + '?q=' + jsonResponse['id']
    uri = url + query

    r = requests.get(uri,
                     headers={"User-Agent": POESESSID,
                              "Content-Type": "application/json",
                              "Accept": "application/json"})

    response = r.json()

    count = 0
    price = 0

    if r.status_code == 200:
        for sellers in response['result']:
            price += convertCurrency(sellers['listing']['price'])
            count += 1
    else:
        print('No trade results found.')
        return 0

    return price / count
