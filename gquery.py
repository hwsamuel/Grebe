from province import Province, Provinces
from gexport import *
import json, ast

def main(out_file, tweets, fields = None, field_delim = '_'):
    out = '[\n'

    for tweet in tweets:
        out += str(ast.literal_eval(json.dumps(tweet)))
        out += ',\n'
    out = out[:-2]+'\n'
    
    if len(out.strip()) == 0:
        return
    
    out += ']'
    f = open(out_file,'w')
    f.write(out)
    f.close()

#tweets = get_tweets(fields='text,coordinates.coordinates,place.full_name,created_at',province=Provinces.AB)
#main(out_file='victor.json', tweets=tweets)

tweets = get_tweets(fields='text,coordinates.coordinates,place.full_name,created_at', start='15-04-2017',province=Provinces.AB)
main(out_file='esha.json', tweets=tweets)

#tweets = get_tweets(fields='text,coordinates.coordinates,place.full_name', keywords="hate myself|no hope|kill myself|fuck myself|destroy myself|hopeless|hopelessness|i am a burden|this is the end")
#main(out_file='nawshad.json', tweets=tweets)