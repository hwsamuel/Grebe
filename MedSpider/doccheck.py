# -*- coding: utf-8 -*-

from lxml import html
from lxml.html.soupparser import fromstring
from datetime import datetime
import re,requests,pandas as pd

class Spidey:
  def __init__(self):
    self.source_id = 2
    self.topic_id = 0
    self.blog_id = 0
    self.comment_id = 0
    self.forum = 'm2m'
    self.NULL = ''

  def get_categories(self):
    categories_df = pd.DataFrame(columns=['id','parent_id','source_id','title','description','url'])
    categories_page = requests.get('http://news.doccheck.com/en/blogs/')
    tree = html.fromstring(categories_page.content)
    categories = tree.xpath("//div[@id='dcHierarchicalCategoryWidget']")[0].xpath(".//a")
    for category in categories:
      title = category.get('title').strip()
      url = category.get('href')
      if title == self.NULL or url == self.NULL:
          continue
      else:
          categories_df.loc[len(categories_df)] = [self.topic_id,self.NULL,self.source_id,title,self.NULL,url]
          self.topic_id += 1
    return categories_df

  def get_topics(self,category_id,category_url):
    topics_df = pd.DataFrame(columns=['id','parent_id','source_id','url','title','description'])
    topics_page = requests.get(category_url)
    tree = html.fromstring(topics_page.content)
    topics = tree.xpath("//div[@class='userblogListingItemInfo']")
    for topic in topics:
      info = topic.xpath(".//div[@class='userblogListingItemTitle']/h2/a")
      if info:
        info = info[0]
        title = info.text.strip()
        url = info.get('href')
      else:
        continue

      description = topic.xpath(".//div[@class='userblogListingItemDescription']/p/text()")
      if description:
        description = description[0].strip().replace('more...','')
      else:
        continue
      topics_df.loc[len(topics_df)] = [self.topic_id,category_id,self.source_id,url,title,description]
      self.topic_id += 1
    return topics_df

  def get_blogs(self,topic_id,topic_url):
    blogs_df = pd.DataFrame(columns=['id','topic_id','source_id','title','body','user_name','last_updated','views','forum','comments'])
    blogs_page = requests.get(topic_url)
    tree = html.fromstring(blogs_page.content)
    blogs = tree.xpath("//div[@class='userblogPostListingItemTitle']/h2/a")
    for blog_link in blogs:
        url = blog_link.get('href')
        title = blog_link.text.strip()
        blog = self._get_blog(url)
        body = blog[0]
        user_name = blog[1]
        last_updated = blog[2]
        num_views = blog[3]
        comments = blog[4]
        blogs_df.loc[len(blogs_df)] = [self.blog_id,topic_id,self.source_id,title,body,user_name,last_updated,num_views,self.forum,comments]
        self.blog_id += 1
    return blogs_df

  def get_comments(self,blog_id,comments_tree):
    comments_df = pd.DataFrame(columns=['id','blog_id','body','user_name','last_updated'])
    for comment in comments_tree:
        body = comment.xpath(".//div[@class='annotationEntryBodyContent']/text()")
        if body:
            body = body[0].strip()
        else:
            continue

        user_name = comment.xpath(".//span[@class='dcAnnotationPerformerName']/a/text()")
        if user_name:
            user_name = user_name[0].strip()
        else:
            user_name = self.NULL

        last_updated = comment.xpath(".//div[@class='dcAnnotationUserInfoContainer']")
        if not last_updated:
            last_updated = self.NULL
        else:
            last_updated = [p.text_content().strip() for p in last_updated]
            if len(last_updated) == 0:
                last_updated = self.NULL
            else:
                last_updated = last_updated[0].strip()
                regex = re.compile("\d{2}\.\d{2}\.\d{4}")
                last_updated = regex.search(last_updated)
                if last_updated == None:
                    last_updated = self.NULL
                else:
                    last_updated = last_updated.group()
                    last_updated = str(datetime.strptime(last_updated,'%d.%m.%Y'))

        comments_df.loc[len(comments_df)] = [self.comment_id,blog_id,body,user_name,last_updated]
        self.comment_id += 1
    return comments_df

  def _get_blog(self,blog_url):
      page = requests.get(blog_url)
      tree = html.soupparser.fromstring(page.content, features='html.parser')
      last_updated = tree.xpath("//div[@class='userblogPostDetailDate']/text()")
      if last_updated:
          last_updated = last_updated[0].strip()
          last_updated = str(datetime.strptime(last_updated,'%d.%m.%Y'))
      else:
          last_updated = self.NULL

      num_views = tree.xpath("//div[@class='userblogPostViewCounter']/text()")
      if num_views:
          num_views = int(num_views[0].strip().replace(' Views',''))
      else:
          num_views = 0

      body_raw = tree.xpath("//div[@itemprop='articleBody']")
      if body_raw:
          body = [p.text_content().strip() for p in body_raw]
      else:
          return None

      if body:
          body = body[0].strip().replace('\n','<br />').replace('\r','<br />').replace('\t',' ')
      else:
          return None

      if body == self.NULL:
          return None

      user_name = tree.xpath("//a[@class='userContactBoxImg']")
      if user_name:
          user_name = user_name[0].get('title').strip()
      else:
          user_name = self.NULL

      comments = tree.xpath("//div[@itemprop='comment']")
      return [body,user_name,last_updated,num_views,comments]

  def crawl(self,dir='doccheck'):
    categories = self.get_categories()
    categories_save = categories.drop('url',axis=1)
    categories_save.to_csv(path_or_buf=dir+'/topics.tsv',sep='\t',index=False,encoding='utf-8')

    blogs_header = True
    comments_header = True

    for cix,category in categories.iterrows():
      topics = self.get_topics(category['id'],category['url'])
      if topics.empty:
        continue
      else:
        topics_save = topics.drop('url',axis=1)
        topics_save.to_csv(path_or_buf=dir+'/topics.tsv',sep='\t',index=False,mode='a',header=False,encoding='utf-8')

        for tix,topic in topics.iterrows():
          blogs = self.get_blogs(topic['id'],topic['url'])
          if blogs.empty:
              continue
          else:
              blogs_save = blogs.drop('comments',axis=1)
              blogs_save.to_csv(path_or_buf=dir+'/blogs.tsv',sep='\t',index=False,mode='a',header=blogs_header,encoding='utf-8')
              blogs_header = False

          for bix,blog in blogs.iterrows():
              tree = blog['comments']
              if len(tree) == 0:
                  continue
              else:
                  comments = self.get_comments(blog['id'],tree)

              comments.to_csv(path_or_buf=dir+'/comments.tsv',sep='\t',index=False,mode='a',header=comments_header,encoding='utf-8')
              comments_header = False

if __name__ == '__main__':
  Spidey().crawl()
