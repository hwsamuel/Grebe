'''
Script to convert Stack Exchange data archive to Kaggle Quora contest format
Datasets are from the Stack Exchange archives https://archive.org/download/stackexchange
'''

from lxml import etree
from random import shuffle
import sys

dataset_folder = sys.argv[1] # Dataset folder must have PostLinks.xml and Posts.xml

mytree = etree.iterparse(dataset_folder+'/PostLinks.xml', events=('end',), tag='row')
duplicate = []
related = []
for ev, p in mytree: # This section parses PostIds and groups them into duplicate or related
    post_id = p.attrib['PostId']
    related_id = p.attrib['RelatedPostId']
    pair = sorted(set([post_id, related_id]))
    type = int(p.attrib['LinkTypeId'])
    
    if type == 3 and pair not in duplicate:
        label = 1
        duplicate.append(pair+[label])
    elif type == 1 and pair not in related and pair not in duplicate:
        label = 0
        related.append(pair+[label])
    
    p.clear()

mytree = etree.iterparse(dataset_folder+'/Posts.xml', events=('end',), tag='row')
posts = {}
for ev, p in mytree: # This section looks up the actual post title using the parsed PostId
    if 'Title' in p.attrib:
        id = p.attrib['Id']
        title = p.attrib['Title'].replace('"',"`").replace("'","`")
        posts[id] = title
    p.clear()

pairs = duplicate+related
shuffle(pairs) # Randomize duplicates and related posts
id = 0
f = open(dataset_folder+'/'+dataset_folder+'.csv', 'w') # Output is stored into a file that matches the dataset folder name with a .csv extension
f.write('"id","qid1","qid2","question1","question2","is_duplicate"\n')
for p in pairs: # This section generates the output
    pid1 = p[0]
    pid2 = p[1]
    label = p[2]
    if pid1 in posts.keys() and pid2 in posts.keys():
        ptt1 = posts[pid1].encode('punycode')[:-1]
        ptt2 = posts[pid2].encode('punycode')[:-1]
        f.write('"' + str(id) + '","' + str(pid1) + '","' + str(pid2) + '","' + str(ptt1) + '","' + str(ptt2) + '","' + str(label) + '"\n')
        id += 1
f.close()