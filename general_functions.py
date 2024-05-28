# transforms an integer into a string (from 00 to 99)
def cardstr(integer):
    prefix = ''
    if int(integer) < 10:
        prefix = '0'
    return prefix + str(integer)

def cardint(string):
    return int(string)
