from province import Province, Provinces
from gexport import *
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def clean(txt):
    if txt == None:
        return None
    else:
        return str(txt).encode('punycode')[:-1].strip().replace('\n', ' ').replace('"', "'")

def main(out_file, tweets, fields = None):
    if fields == None:
        fields = 'tweet, longitude, latitude, created_at, place_name'
    
    out = '[\n'
    for tweet in tweets:
        i = 0
        out += "\t{\n"
        for field in fields.split(','):
            text = tweet[i]
            if text == None:
                text = ""
            else:
                text = clean(text)
            out += '\t\t"' + field.strip() + '":"' + text + '",\n'
            i += 1
        out = out[:-2] + "\n\t},\n"
    out = out[:-2]+'\n'
    
    if len(out.strip()) == 0:
        return
    
    out += ']'
    f = open(out_file,'w') # Validated JSON (RFC-4627, RFC-7159, ECMA-404) https://jsonformatter.curiousconcept.com/
    f.write(out)
    f.close()

def tsv(out_file, tweets, fields = None):
    if fields == None:
        fields = 'tweet, longitude, latitude, created_at, place_name'
    
    out = fields.replace(',', '\t')+'\n'
    for tweet in tweets:
        i = 0
        for field in fields.split(','):
            text = tweet[i]
            if text == None:
                text = ""
            else:
                text = clean(text)
            out += text + '\t'
            i += 1
        out = out[:-1] + '\n'

    if len(out.strip()) == 0:
        return

    f = open(out_file,'w')
    f.write(out)
    f.close()

fields = "user_id, id, created_at, tweet"

tweets = get_tweets(keywords="#depressed", fields=fields, strict=False)
tsv(out_file='exports/depression.tsv', fields=fields, tweets=tweets)