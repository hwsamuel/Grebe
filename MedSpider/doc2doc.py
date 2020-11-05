# -*- coding: utf-8 -*-

from lxml import html
from lxml.html.soupparser import fromstring
from datetime import datetime
import requests,pandas as pd

class Spidey:
    def __init__(self):
        self.source_id = 1
        self.topic_id = 0
        self.thread_id = 0
        self.discussion_id = 0
        self.forum = 'm2m'
        self.NULL = ''

    def get_categories(self):
        categories_df = pd.DataFrame(columns=['id','parent_id','source_id','title','description','topics'])
        categories_page = requests.get('https://web.archive.org/web/20160615110148/http://doc2doc.bmj.com/forumhome.html')
        tree = html.fromstring(categories_page.content)
        categories = tree.xpath("//div[@class='category']")
        for category in categories:
            title = category.xpath(".//h2/text()")
            if title:
                title = title[0].strip()
            else:
                continue

            if title == self.NULL:
                continue

            if title not in categories_df['title'].tolist():
                categories_df.loc[len(categories_df)] = [self.topic_id,self.NULL,self.source_id,title,self.NULL,category]
                self.topic_id += 1
        return categories_df

    def get_topics(self,category_id,tree):
        topics_df = pd.DataFrame(columns=['id','parent_id','source_id','url','title','description'])
        topics = tree.xpath(".//div[@class='forum']/div")
        for topic in topics:
            url = topic.xpath(".//h3/a")
            if url:
                url = 'https://web.archive.org'+url[0].get('href')
            else:
                continue

            title = topic.xpath(".//h3/a/text()")
            if title:
                title = title[0].strip()
            else:
                continue

            if title == self.NULL:
                continue

            description = topic.xpath(".//p/text()")
            if description:
                description = description[0]
            else:
                description = self.NULL
            if title not in topics_df['title'].tolist():
                topics_df.loc[len(topics_df)] = [self.topic_id,category_id,self.source_id,url,title,description]
                self.topic_id += 1
        return topics_df

    def get_threads(self,topic_id,topic_url):
        threads_df = pd.DataFrame(columns=['id','source_id','topic_id','url','views','forum'])
        topic_page = requests.get(topic_url)
        tree = html.fromstring(topic_page.content)
        threads = tree.xpath("//div[@class='pluck-forums-main-discussion-inner-wrap']")
        for thread in threads:
            link = thread.xpath(".//a[contains(@class,'pluck-forums-discussion-title-link')]")
            if link:
                url = link[0].get('href').strip()
                title = link[0].get('title').strip()
            else:
                continue

            if title == self.NULL or url == self.NULL:
                continue

            try:
                num_views = thread.xpath(".//div[@class='pluck-forums-main-discussion-views-col']/p[@class='pluck-forums-cat-discussion-number']/text()")
                num_views = int(num_views[0].strip())
            except Exception:
                num_views = 0
            
            if url not in threads_df['url'].tolist():
                threads_df.loc[len(threads_df)] = [self.thread_id,self.source_id,topic_id,url,num_views,self.forum]
                self.thread_id += 1
        return threads_df

    def get_discussions(self,thread_id,thread_url):
        discussions_df = pd.DataFrame(columns=['id','thread_id','body','user_name','last_updated','upvotes','downvotes'])
        discussion_page = requests.get(thread_url)
        try:
            tree = html.soupparser.fromstring(discussion_page.content, features='html.parser')
        except Exception:
            return discussions_df

        discussions = tree.xpath("//div[contains(@class,'pluck-forums-main-forumpost-wrap')]")
        for discussion in discussions:
            body_raw = discussion.xpath(".//div[@class='pluck-forums-forumpost-text']")
            if body_raw:
                body = [p.text_content().strip() for p in body_raw]
            else:
                continue

            if body:
                body = body[0].strip().replace('\n','<br />').replace('\r','<br />').replace('\t',' ')
            else:
                continue

            if body == self.NULL:
                continue

            user_name = discussion.xpath(".//div[@class='pluck-forums-forumpost-username']/a/text()")
            if len(user_name) == 0:
                user_name = self.NULL
            else:
                user_name = user_name[0].strip()

            last_updated = discussion.xpath(".//p[@class='pluck-forums-main-forumpost-timestamp']/a/text()")
            if len(last_updated) == 0:
                last_updated = self.NULL
            else:
                last_updated = last_updated[0].strip().replace(', ', ' ')
                last_updated = str(datetime.strptime(last_updated,'%d/%m/%Y %I:%M %p'))

            votes = discussion.xpath(".//span[@class='pluck-score-volume pluck-score-has-info']")
            if len(votes) == 0:
                upvotes = 0
                downvotes = 0
            else:
                upvotes = int(votes[0].get('upvotes'))
                downvotes = int(votes[0].get('downvotes'))

            if body not in discussions_df['body'].tolist():
                discussions_df.loc[len(discussions_df)] = [self.discussion_id,thread_id,body,user_name,last_updated,upvotes,downvotes]
                self.discussion_id += 1
        return discussions_df

    def crawl(self,dir='doc2doc'):
        categories = self.get_categories()
        categories_save = categories.drop('topics',axis=1)
        categories_save.to_csv(path_or_buf=dir+'/topics.tsv',sep='\t',index=False,encoding='utf-8')

        threads_header = True
        discussions_header = True

        for cix,category in categories.iterrows():
            topics = self.get_topics(category['id'],category['topics'])
            if topics.empty:
                continue
            else:
                topics_save = topics.drop('url',axis=1)
                topics_save.to_csv(path_or_buf=dir+'/topics.tsv',sep='\t',index=False,mode='a',header=False,encoding='utf-8')

            for tix,topic in topics.iterrows():
                threads = self.get_threads(topic['id'],topic['url'])
                if threads.empty:
                    continue
                else:
                    threads_save = threads.drop('url',axis=1)
                    threads_save.to_csv(path_or_buf=dir+'/threads.tsv',sep='\t',index=False,mode='a',header=threads_header,encoding='utf-8')
                    threads_header=False

                for ixt,thread in threads.iterrows():
                    discussions = self.get_discussions(thread['id'],thread['url'])
                    if discussions.empty:
                        continue
                    else:
                        discussions.to_csv(path_or_buf=dir+'/discussions.tsv',sep='\t',index=False,mode='a',header=discussions_header,encoding='utf-8')
                        discussions_header=False

if __name__ == '__main__':
    Spidey().crawl()
