import base64

def readFile (path):
    # read file in given path and returns contents in string
    # args: path - path of file to read

    try:
        dataFile = open(path, "r")
        
    except Exception as e:
        return f"Could not find file to read. Exception: {e}"

    dataFileContent = dataFile.read()
    dataFile.close()
    return dataFileContent


def base64EncodeScript(script):
    # convert script to utf-8 bytes and encodes in base64 format
    # convert back to string by decoding utf-8 and return

    return base64.b64encode(bytes(script, 'utf-8')).decode('utf-8')