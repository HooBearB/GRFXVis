def loadFile(filepath : str, debug : bool = False):
    try:
        file = open(filepath, "r")
        lines = file.readlines()
        data = []
        for line in lines:
            if debug:
                print(f"\nfulline {line}")
            if line != "":
                data.append(readLine(line, debug))
        return data
    except Exception as error:
        print(f"mGRFXLib: loadFile() has encountered {error}, returning none")
        return None
    
def readTag(tag : str, debug : bool = False):
    headers = {"m": "int", "s": "float", "x": "int", "y": "int", "l": "str", "p": "str"}
    tagData = {}
    enter = 0
    while enter < len(tag):
        if tag[enter] in headers.keys():
            header = tag[enter]
            exit = enter + 1
            while tag[exit] != ";":
                exit = exit + 1
                if exit >= len(tag):
                    break
            tagData[header] = tag[enter + 1 : exit]
            if headers[header] != "str":
                if tagData[header] != "":
                    if headers[header] == "float":
                        tagData[header] = float(tagData[header])
                    elif headers[header] == "int":
                        tagData[header] = int(tagData[header])
                else:
                    tagData[header] = 0
            enter = exit
        enter = enter + 1
    total = 0
    if "m" in tagData.keys():
        total = total + tagData["m"] * 60
    if "s" in tagData.keys():
        total = total + tagData["s"]
    tagData["t"] = total
    return tagData

def readLine(line, debug : bool = False):
    start = 0
    rawData = []
    while start < len(line):
        if line[start] == "<":
            end = start + 1
            while line[end] != "<" and end + 1 < len(line):
                end = end + 1
            if debug:
                print(f"contentline {line[start:end]}")
            rawData.append(line[start:end])
            start = end - 1
        start = start + 1
    data = []
    for rawObject in rawData:
        if debug:
            print(f"tagline {rawObject[1:rawObject.find('>')]}")
        object = readTag(rawObject[:rawObject.find(">")], debug)
        object["content"] = rawObject[rawObject.find(">") + 1:]
        data.append(object)
    return data