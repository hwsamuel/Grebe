# -*- coding: utf-8 -*-

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
        return tree.xpath("//a[@class='link']")

    def _get_discussions(self,url):
        discussions = []
        page = requests.get(url)
        tree = html.fromstring(page.content)

        num_posts = tree.xpath("//table[@class='base'][1]/tr[2]/td[3]/text()")
        if len(num_posts) == 0:
            return discussions
        
        num_posts = int(num_posts[0].encode('punycode')[:-1].strip())
        pages = int(math.ceil(num_posts/100))+1
        
        for i in range (1, pages+1):
            elements = tree.xpath("//table[@class='base'][2]/tr/td[2]/b/a")
            for element in elements:
                discuss_url = element.get('href')
                title = element.text
                new_discuss = [discuss_url, title]
                discussions.append(new_discuss)
            page = requests.get(url+'?page='+str(i+1))
            tree = html.fromstring(page.content)
        return discussions

    def _get_posts(self,url):
        page = requests.get(url)
        tree = html.fromstring(page.content)
        
        element = tree.xpath("//table[@class='base2']")[0]
        date1 = element.xpath(".//tr[2]/td[1]/text()")[0]
        body1 = element.xpath(".//tr[2]/td[2]/span/text()")[0].encode('punycode')[:-1]
        
        date2 = element.xpath(".//tr[4]/td[1]/text()")
        body2 = element.xpath(".//tr[4]/td[2]/span/text()")
        if len(date2) == 0 or len(body2) == 0:
            return []
        date2 = date2[0]
        body2 = body2[0].encode('punycode')[:-1]
        new_post = [date1,body1,date2,body2]
        return new_post
        
    def crawl(self,dir='hopkins'):
        base = 'http://www.hopkinsbreastcenter.org'
        main_url = base+'/services/ask_expert'
        forums = self._get_forums(main_url)
        
        f = open(dir+'/discussions.tsv', 'w')
        f.write('forum_name\tdiscussion_title\tdiscussion_url\tquestion_date\tquestion\tanswer_date\tanswer\n')
        
        for forum in forums:
            forum_url = base+forum.get('href')
            forum_name = forum.text
            forum_id = sha1(forum_url).hexdigest()
            
            discussions = self._get_discussions(forum_url)
            for discussion in discussions:
                discuss_url = base+discussion[0]
                discuss_title = discussion[1]
                discuss_id = sha1(discuss_url).hexdigest()
                
                post = self._get_posts(discuss_url)
                if len(post) == 0:
                    continue
                question_date = post[0]
                question = post[1]
                answer_date = post[2]
                answer = post[3]
                f.write(forum_name+'\t'+discuss_title+'\t'+discuss_url+'\t'+question_date+'\t'+question+'\t'+answer_date+'\t'+answer+'\n')
        f.close()

class TestSpidey(object):
    def test_get_forums(self):
        assert len(Spidey()._get_forums('http://www.hopkinsbreastcenter.org/services/ask_expert/')) == 30
        
    def test_get_discussions1(self):
        assert len(Spidey()._get_discussions('http://www.hopkinsbreastcenter.org/services/ask_expert/family_support/')) == 151
    
    def test_get_discussions2(self):
        assert len(Spidey()._get_discussions('http://www.hopkinsbreastcenter.org/services/ask_expert/questions_to_ask_to_ensure_you_are_in_good_hands/')) == 2430
        
    def test_get_posts1(self):
        assert len(Spidey()._get_posts('http://www.hopkinsbreastcenter.org/services/ask_expert/viewquestions.asp?id=999844068')) == 4
    
    def test_get_posts2(self):
        assert len(Spidey()._get_posts('http://www.hopkinsbreastcenter.org/services/ask_expert/viewquestions.asp?id=999844124')) == 4
    
if __name__ == '__main__':
    Spidey().crawl()