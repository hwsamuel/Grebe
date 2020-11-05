# -*- coding: utf-8 -*-

from lxml import html
from lxml.html.soupparser import fromstring
from hashlib import sha1
from re import split
import requests, sys, math

reload(sys)
sys.setdefaultencoding('utf-8')

class Spidey:
    def _get_yearly_listings(self,url):
        page = requests.get(url)
        tree = html.fromstring(page.content)
        return tree.xpath("//a[@class='subcategory_link']")

    def _get_chat_listings(self,url):
        page = requests.get(url)
        tree = html.fromstring(page.content)

        listings = []
        elements = tree.xpath("//font/b/a")
        for element in elements:
            listing_url = element.get('href').strip()
            listing_title = element.get('title').strip()
            title_text = element.xpath('.//text()')
            new_listing = [listing_url, listing_title, title_text]
            listings.append(new_listing)
        return listings

    def _get_chats(self,url):
        page = requests.get(url)
        tree = html.soupparser.fromstring(page.content, features='html.parser')

        posts = []
        elements = tree.xpath("//table[preceding::h1]/tr")
        for element in elements:
            timestamp = element.xpath(".//td[contains(@style,'color:#888;')]/text()")
            username = element.xpath(".//td/em/text()")
            message = element.xpath(".//td/strong/text()")
            if len(timestamp) > 0 and len(username) > 0 and len(message) > 0:
                new_post = [timestamp[0], username[0].encode('punycode'), message[0]]
                posts.append(new_post)
        return posts

    def crawl(self,dir='ohn'):
        base = 'https://web.archive.org' 
        main_url = base+'/web/20130129082319/http://www.optimalhealthnetwork.com/Alternative-Health-Live-Chat-Log-Archive-s/196.htm'

        year_listings = self._get_yearly_listings(main_url)
        
        f = open(dir+'/chats.tsv', 'w')
        f.write('thread_id\tchat_title\tdate\ttimestamp\tuser\tmessage\n')
        for year_listing in year_listings:
            chat_listing_url = year_listing.get('href')
            chat_listings = self._get_chat_listings(chat_listing_url)
            for chat_listing in chat_listings:
                chat_url = chat_listing[0]
                chat_title = chat_listing[1]
                date = chat_listing[2][0][21:].strip()
                chats = self._get_chats(chat_url)
                id = sha1(chat_title+date).hexdigest()
                for chat in chats:
                    f.write(id+'\t'+chat_title+'\t'+date+'\t'+chat[0]+'\t'+chat[1]+'\t'+chat[2]+'\n')
        f.close()

class TestSpidey(object):
    def test_get_yearly_listings(self):
        assert len(Spidey()._get_yearly_listings('https://web.archive.org/web/20130129082319/http://www.optimalhealthnetwork.com/Alternative-Health-Live-Chat-Log-Archive-s/196.htm')) == 9
        
    def test_get_chat_listings(self):
        assert len(Spidey()._get_chat_listings('https://web.archive.org/web/20120212091416/https://www.optimalhealthnetwork.com/Alternative-Health-Live-Chat-Log-Archive-2012-s/793.htm')) == 4
        
    def test_get_chats(self):
        assert len(Spidey()._get_chats('https://web.archive.org/web/20120209041230/http://www.optimalhealthnetwork.com/Healing-with-Essential-Oils-Alternative-Health-Live-Chat-s/794.htm')) == 102
        
if __name__ == '__main__':
    Spidey().crawl()