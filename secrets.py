def get_secrets():
    secretresult = {}
    with open('./secrets.txt') as file:
        for line in file:
            _line = line.split("=")
            secretresult[_line[0]] = _line[1]
    return secretresult