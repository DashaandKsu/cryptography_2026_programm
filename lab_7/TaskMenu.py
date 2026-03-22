def startup(cypher_name, values_dict):
    print(f'Welcome to the {cypher_name} cypher.')
    mode = input('Would you like to:\n1) Encrypt custom text\n2) Decrypt custom text\n3) Make 1000-char test\n')
    for key in values_dict:
        values_dict[key] = input(f'Please, enter your {key}: ')
    return mode, values_dict


def getline(filename, convert=False, codec='UTF-8'):
    with open(filename, encoding=codec) as source:
        line = source.read()
    if convert:
        return bytearray(line, codec).hex()
    return line
