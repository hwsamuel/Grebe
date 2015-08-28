'''
    Helper functions
'''

from re import split,compile

def load_thesaurus(filename):
    thes = {}
    with open(filename) as fp:
        f = fp.read()     
        line = ''
        for char in f:
            if char != '\r':
                line += char
            else:
                line = line.split(',')
                for word in line[1:]:
                    thes.setdefault(line[0], []).append(word)
                line = ''
    return thes

def load_file(file):
    f = open(file)
    valid_lines = []
    for line in f.readlines():
        line = line.strip().lower()
        if line is not '':
            valid_lines.append(line)
    return valid_lines

def flatten(list_of_lists):
    return [val for sublist in list_of_lists for val in sublist]

def deduplicate(lst):
    seen = set()
    seen_add = seen.add
    return [x for x in lst if not (x in seen or seen_add(x))]

def tokenize(sentence):
    return compile("[^a-zA-Z0-9']").split(sentence)