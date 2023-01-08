import json
import re


def UniqueMods(inputMods):
    with open('./data/modList.json') as file:
        modList = json.load(file)

    filteredMods= []
    filteredValues = []
    cleanedMods = []
    modId = []
    for i in range(len(inputMods)):
        modId.append('Not Found')

    for inputMod in inputMods:
        filteredValues.append(re.findall('\\d+', inputMod))
        filteredMods.append(re.sub('\\d+', '#', inputMod))

    cleanedMods = []
    for idx, mod in enumerate(filteredMods):
        clean = mod.replace('(#-#)', '#')
        cleanedMods.append(clean)

    for idx, inMod in enumerate(cleanedMods):
        for mod in modList['data']:
            if mod['ref'] == inMod:
                modId[idx] = (mod['trade']['ids']['explicit'])
                break

    return filteredValues, modId
