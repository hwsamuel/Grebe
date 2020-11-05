# -*- coding: utf-8 -*-
# 'Ask a Doctor' forum discussions are scraped for patient-doctor threads, patient-patient discussions are ignored

from lxml import html
from lxml.html.soupparser import fromstring
from hashlib import sha1
from re import split
import requests, sys, math

reload(sys)
sys.setdefaultencoding('utf-8')

class Spidey:
    def _get_forums(self,url):
        page = requests.get(url)
        tree = html.fromstring(page.content)
        return tree.xpath("//div[@class='forums_forum_name']/a")

    def _get_discussions(self,url):
        page = requests.get(url)
        tree = html.fromstring(page.content)

        discussions = []
        elements = tree.xpath("//a[@class='topictitle']")
        for element in elements:
            discuss_url = element.get('href')
            title = element.text
            new_discuss = [discuss_url, title]
            discussions.append(new_discuss)
        return discussions

    def _get_posts(self,url):
        page = requests.get(url)
        tree = html.fromstring(page.content)

        posts = []
        elements = tree.xpath("//div[@class='vt_post_holder']")
        for element in elements:
            user = element.xpath(".//span[@class='vt_asked_by_user']/a")
            if len(user) == 0:
                user = element.xpath(".//div[@class='vt_asked_by_user']/a")
            
            if len(user) == 0:
                continue
            else:
                user = user[0].text.strip()
            
            date = element.xpath(".//span[@class='vt_first_timestamp']")
            if len(date) == 0:
                date = element.xpath(".//div[@class='vt_reply_timestamp']")
            date = date[0].text.strip().replace('replied ','')
            
            body = element.xpath(".//div[@class='vt_post_body']/text()")
            body = '\n'.join(body).strip().replace('\t','').replace('\n','').replace('\r','').encode('punycode')[:-1]
            
            id = sha1(user+date+body).hexdigest()
            new_post = [id,user,date,body]
            posts.append(new_post)
        return posts

    def crawl(self,dir='ehealthforum'):
        base = 'https://ehealthforum.com/health/' 
        main_url = base+'ask_a_doctor_forums.html'

        forums = self._get_forums(main_url)

        f = open(dir+'/chats.tsv', 'w')
        f.write('forum_id\tforum_name\tdiscussion_id\tdiscussion_title\tdiscussion_url\tpost_id\tposted_date\tuser_name\tcontent\n')
        
        for forum in forums:
            forum_url = base+forum.get('href')
            forum_name = forum.text
            forum_id = sha1(forum_url).hexdigest()

            discussions = self._get_discussions(forum_url)
            for discussion in discussions:
                discuss_url = discussion[0]
                discuss_title = discussion[1]
                discuss_id = sha1(discuss_url).hexdigest()
                
                posts = self._get_posts(discuss_url)
                for post in posts:
                    post_id = post[0]
                    post_user = post[1]
                    post_date = post[2]
                    post_content = post[3]
                    f.write(forum_id+'\t'+forum_name+'\t'+discuss_id+'\t'+discuss_title+'\t'+discuss_url+'\t'+post_id+'\t'+post_date+'\t'+post_user+'\t'+post_content+'\n')
        f.close()

class TestSpidey(object):
    def test_get_forums(self):
        assert len(Spidey()._get_forums('https://ehealthforum.com/health/ask_a_doctor_forums.html')) == 199
        
    def test_get_discussions(self):
        assert len(Spidey()._get_discussions('https://ehealthforum.com/health/doctor_questions_169.html')) == 9
        
    def test_get_posts(self):
        assert len(Spidey()._get_posts('https://ehealthforum.com/health/i-need-help-i-drink-every-night-t281246.html')) == 2
    
if __name__ == '__main__':
    Spidey().crawl()