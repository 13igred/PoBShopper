import base64
import re
import zlib
import xmltodict


def filterUniqueMods(item):
    # remove mod range from string
    item['#text'] = re.sub('{range:(.*)}', '', item['#text'])

    text = item['#text'].split('\n')
    modLineImplicit = []
    modLineExplicit = []

    defineType = re.search('variant:\d+,', item['#text'])

    if defineType:
        # select variant
        for itemLine in text:
            if 'Selected Variant:' in itemLine:
                for c in itemLine:
                    if c.isdigit():
                        selectedVariant = int(c)

        numImplicits = 0
        idxImplicit = 0
        for idx, itemLine in enumerate(text):
            # find if mod is implicit or explicit
            # find implicits / rolls
            if 'Implicits: ' in itemLine:
                idxImplicit = idx
                for m in itemLine:
                    if m.isdigit():
                        numImplicits = int(m)
                        idxImplicit = idx

            # find variants
            if 'variant:' in itemLine:
                extracted = re.findall('{variant:(.*)}', itemLine)
                if len(itemLine) > 0:
                    for c in extracted[0]:
                        if c.isdigit():
                            if int(c) == selectedVariant:
                                itemLine = re.sub('{variant:(.*)}', '', itemLine)
                                if idx <= idxImplicit + numImplicits:
                                    modLineImplicit.append(itemLine)
                                else:
                                    modLineExplicit.append(itemLine)
    else:
        multiVariant = []
        for idx, itemLine in enumerate(text):
            if 'Selected Variant:' in itemLine:
                matched = re.search(r'\d+', itemLine).group()
                multiVariant.append(int(matched))
            if 'Selected Alt Variant: ' in itemLine and 'Has Alt Variant: true' in text[idx - 1]:
                matched = re.search(r'\d+', itemLine).group()
                multiVariant.append(int(matched))
            if 'Selected Alt Variant Two: ' in itemLine and 'Has Alt Variant Two: true' in text[idx - 1]:
                matched = re.search(r'\d+', itemLine).group()
                multiVariant.append(int(matched))

        # find variants
        for value in multiVariant:
            found = False
            for itemLine in text:
                if found:
                    break
                if 'variant:' in itemLine:
                    matched = re.search(r'\d+', itemLine).group()
                    if int(matched) == value:
                        itemLine = re.sub('{variant:(.*)}', '', itemLine)
                        modLineExplicit.append(itemLine)
                        found = True
                        break

    links = 0
    implicits = []
    explicits = []
    # find if item is unique
    if 'Rarity: UNIQUE' in item['#text']:
        numImplicits = 0
        idxImplicit = 0

        for idx, t in enumerate(text):
            # find links
            if 'Sockets: ' in t:
                # if its a 6 socket
                if len(t) == 20:
                    links = 6

            # find implicits / rolls
            if 'Implicits: ' in t:
                idxImplicit = idx
                for m in t:
                    if m.isdigit():
                        numImplicits = int(m)

        # add implicits
        if len(modLineImplicit) > 0:
            for modd in modLineImplicit:
                implicits.append(modd)
        else:
            for i in range(numImplicits):
                implicits.append(text[idxImplicit + i + 1])

        # add explicits
        if len(modLineExplicit) > 0:
            for modd in modLineExplicit:
                explicits.append(modd)
        else:
            for i in range(len(text) - (idxImplicit + numImplicits + 1)):
                explicits.append(text[i + idxImplicit + numImplicits + 1])

        itemName = text[1]

        uniqueDict = {
            'name': itemName,
            'links': links,
            'implicits': implicits,
            'explicits': explicits,
            'tradeUrl': '',
            'price': 0
        }

        return uniqueDict

def skillData(skills, title='default'):
    buildDict = {'name': title, 'gems': []}
    for i in skills['Skill']:
        if isinstance(i['Gem'], list):
            for j in i['Gem']:
                support = 0
                if 'Support' in j['@skillId']:
                    support = 1
                gemList = {
                    'name': j['@nameSpec'],
                    'quality': j['@quality'],
                    'type': j['@qualityId'],
                    'level': j['@level'],
                    'support': support,
                    'tradeUrl': '',
                    'price': 0
                }
                buildDict['gems'].append(gemList)
        else:
            j = i['Gem']
            support = 0
            gemType = 'none'

            if 'Support' in j['@skillId']:
                support = 1

            if '@qualityId' in j:
                gemType = i['Gem']['@qualityId']

            gemList = {
                'name': i['Gem']['@nameSpec'],
                'quality': i['Gem']['@quality'],
                'type': gemType,
                'level': i['Gem']['@level'],
                'support': support,
                'tradeUrl': '',
                'price': 0
            }
            buildDict['gems'].append(gemList)

    return buildDict


class POB:
    def __init__(self, base64String):
        base64_decode = base64.urlsafe_b64decode(base64String)
        decoded = zlib.decompress(base64_decode).decode('utf-8')
        self.pob = xmltodict.parse(decoded)
        self.gems = self.extractGems()
        self.uniques = self.extractUniques()

    def extractGems(self):
        buildGems = []
        skills = self.pob['PathOfBuilding']['Skills']['SkillSet']
        if isinstance(skills, list):
            for s in skills:
                buildGems.append(skillData(s, s['@title']))
        else:
            buildGems.append(skillData(skills))

        return buildGems

    def extractUniques(self):
        # Todo: write code to fix variants
        uniques = []
        items = self.pob['PathOfBuilding']['Items']['Item']
        for item in items:
            if 'UNIQUE' in item['#text']:
                uniqueDict = filterUniqueMods(item)
                uniques.append(uniqueDict)

        return uniques

    def totalPriceEstimate(self):
        totalCost = 0
        for gems in self.gems:
            for gem in gems['gems']:
                totalCost += gem['price']

        for unique in self.uniques:
            totalCost += unique['price']

        return totalCost
