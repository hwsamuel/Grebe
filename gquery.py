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

def tsv(out_file, tweets, fields = None, separator = '\t', show_header = True):
    if fields == None:
        fields = 'tweet, longitude, latitude, created_at, place_name'
    
    if show_header:
        out = fields.replace(',', separator)+'\n'
    else:
        out = ''

    for tweet in tweets:
        i = 0
        for field in fields.split(','):
            text = tweet[i]
            if text == None:
                text = ''
            else:
                text = clean(text)
            out += text + separator
            i += 1
        out = out[:-1] + '\n'

    if len(out.strip()) == 0:
        return

    f = open(out_file,'w')
    f.write(out)
    f.close()

def format_unixtime(tweets):
    new_tweets = []
    for tweet in tweets:
        new_tweet = []
        new_tweet.append(tweet[0])
        new_tweet.append(tweet[1])
        new_tweet.append(int(time.mktime(tweet[2].timetuple())))
        new_tweet.append(tweet[3])
        new_tweets.append(new_tweet)
    return new_tweets

fields = "user_id, id, created_at, tweet"

if __name__ == '__main__':
	print get_tweets(province='Alberta')
	'''tweets = format_unixtime(get_tweets(keywords="#depressed", fields=fields, strict=False))
	tsv(out_file='exports/depression.txt', fields=fields, tweets=tweets, separator=' ', show_header=False)

	tweets = format_unixtime(get_tweets(keywords="#deception", fields=fields, strict=False))
	tsv(out_file='exports/deception.txt', fields=fields, tweets=tweets, separator=' ', show_header=False)

	tweets = format_unixtime(get_tweets(keywords="#schadenfreude", fields=fields, strict=False))
	tsv(out_file='exports/schadenfreude.txt', fields=fields, tweets=tweets, separator=' ', show_header=False)

	tweets = format_unixtime(get_tweets(keywords="#frustrated", fields=fields, strict=False))
	tsv(out_file='exports/frustrated.txt', fields=fields, tweets=tweets, separator=' ', show_header=False)

	tweets = format_unixtime(get_tweets(keywords="#frustration", fields=fields, strict=False))
	tsv(out_file='exports/frustration.txt', fields=fields, tweets=tweets, separator=' ', show_header=False)

	tweets = format_unixtime(get_tweets(keywords="#disappointed", fields=fields, strict=False))
	tsv(out_file='exports/disappointment.txt', fields=fields, tweets=tweets, separator=' ', show_header=False)

	tweets = format_unixtime(get_tweets(keywords="#hopelessness", fields=fields, strict=False))
	tsv(out_file='exports/hopelessness.txt', fields=fields, tweets=tweets, separator=' ', show_header=False)

	tweets = format_unixtime(get_tweets(keywords="#discontent", fields=fields, strict=False))
	tsv(out_file='exports/discontent.txt', fields=fields, tweets=tweets, separator=' ', show_header=False)

	tweets = format_unixtime(get_tweets(keywords="#betrayed", fields=fields, strict=False))
	tsv(out_file='exports/betrayed.txt', fields=fields, tweets=tweets, separator=' ', show_header=False)

	tweets = format_unixtime(get_tweets(keywords="#compassion", fields=fields, strict=False))
	tsv(out_file='exports/compassion.txt', fields=fields, tweets=tweets, separator=' ', show_header=False)

	tweets = format_unixtime(get_tweets(keywords="#selfhate|#ihatemyself|#ifuckmyself|i hate myself|i fuck myself", fields=fields, strict=False))
	tsv(out_file='exports/selfloath.txt', fields=fields, tweets=tweets, separator=' ', show_header=False)

	tweets = format_unixtime(get_tweets(keywords="#rejected|#rejection|nobody wants me|everyone rejects me", fields=fields, strict=False))
	tsv(out_file='exports/rejected.txt', fields=fields, tweets=tweets, separator=' ', show_header=False)

	tweets = format_unixtime(get_tweets(keywords="#lonely|#loner|i am alone", fields=fields, strict=False))
	tsv(out_file='exports/lonely.txt', fields=fields, tweets=tweets, separator=' ', show_header=False)

	tweets = format_unixtime(get_tweets(keywords="#hopeless|no hope|end of a tunnel|end of everything", fields=fields, strict=False))
	tsv(out_file='exports/hopeless.txt', fields=fields, tweets=tweets, separator=' ', show_header=False)

	tweets = format_unixtime(get_tweets(keywords="I have been diagnosed with depression|I am diagnosed with depression|I was diagnosed with depression|Doctor diagnosed me with depression", fields=fields, strict=False))
	tsv(out_file='exports/depressiondisclosure.txt', fields=fields, tweets=tweets, separator=' ', show_header=False)'''
