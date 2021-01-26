import string
import random

def rand_password():
    l = 10
    stringset = string.ascii_lowercase
    result=""
    for i in range(l):
        result += random.choice(stringset)
    return result
