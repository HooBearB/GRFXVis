def loadFile(filepath):
    try:
        file = open(filepath)
        lines = file.readlines()
        data = []
        iter = 0
        for line in lines:
            linecontent = readLine(line)
            for item in linecontent:
                item["id"] = iter
                iter = iter + 1
            data = data + linecontent
        print(f"mGRFXVis: loadFile() loaded {filepath} properly")
        return data
    except:
        print("mGRFXLib: loadFile() has encountered an error, returning none")
        return None
    
def readTag(tag):
    headers = {"m": "float", "s": "float", "x": "int", "y": "int", "f": "int", "l": "int", "h": "int", "q": "int"}
    tagData = {}
    char = 0
    while char < len(tag):
        if tag[char] in headers.keys():
            header = tag[char]
            iter = (char + 1)
            while tag[iter] not in headers.keys():
                iter = iter + 1
                if iter >= len(tag) - 1:
                    break
            
            tagData[header] = tag[char + 1:iter]
            if headers[header] == "float":
                tagData[header] = float(tagData[header])
            if headers[header] == "int":
                tagData[header] = int(tagData[header])
        char = char + 1
    if "m" in tagData.keys():
        if "s" in tagData.keys():
            tagData["t"] = (tagData["m"] * 60) + tagData["s"]
        else:
            tagData["t"] = tagData["m"] * 60
    elif "s" in tagData.keys():
        tagData["t"] = tagData["s"]
    return tagData

def readLine(line):
    iter = 0
    rawdata = []
    while iter < len(line):
        if line[iter] == "<":
            end = iter + 1
            while line[end] != "<" and end + 1 < len(line):
                end = end + 1
            rawdata.append(line[iter:end])
            iter = end - 1
        iter = iter + 1
    data = []
    for rawObject in rawdata:
        object = readTag(rawObject[:rawObject.find(">") + 1])
        object["content"] = rawObject[rawObject.find(">") + 1:]
        data.append(object)
    return data