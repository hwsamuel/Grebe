# -*- coding: utf-8 -*-

from lxml import html
from lxml.html.soupparser import fromstring
from hashlib import sha1
from re import split
from requests.exceptions import ConnectionError
import requests, sys, math, time
import pandas as pd

reload(sys)
sys.setdefaultencoding('utf-8')

class Spidey:
    paging = 50

    def _get_pages(self,url):
        try:
            page = requests.get(url)
        except ConnectionError as ce:
            print ce
            return 0

        tree = html.fromstring(page.content)
        num_questions = tree.xpath("//div[contains(@class,'mr12')]/text()")
        if num_questions:
            num_questions = num_questions[2].split()[0].strip()
        else:
            return 0
        
        num_questions = int(num_questions.replace(',',''))
        extra = num_questions % self.paging
        if extra > 0:
            extra = 1
        return (num_questions/self.paging) + extra

    def _get_question_links(self,base,url):
        question_links = ""
        try:
            page = requests.get(base+url)
        except ConnectionError as ce:
            print ce
            return question_links

        tree = html.fromstring(page.content)

        list_questions = tree.xpath("//div[@class='summary']/h3/a[@class='question-hyperlink']")
        if len(list_questions) == 0:
            return list_questions

        for q in list_questions:
            question_links += base + q.get('href') + ","
        return question_links

    def _get_question_details(self,tree):
        qtitle = tree.xpath("//h1[@itemprop='name']/a/text()")
        if qtitle:
            qtitle = qtitle[0]
        else:
            return None
        qbody = tree.xpath("//div[contains(@class,'postcell')]/div/p/text()")
        qbody = ' '.join(qbody).replace('\n','<br />').replace('\r','<br />').replace('\t',' ')
        qbody = qbody.encode('punycode')
        qtimestamp = tree.xpath("//span[@class='relativetime']")
        if qtimestamp:
            qtimestamp = qtimestamp[0].get('title')
        else:
            qtimestamp = ''
        quser = tree.xpath("//div[@class='user-details']/a/text()")
        if quser:
            quser = quser[0]
        else:
            quser = ''
        qvote = tree.xpath("//div[@itemprop='upvoteCount']/text()")
        if qvote:
            qvote = int(qvote[0])
        else:
            qvote = ''
        qfavorite = tree.xpath("//div[contains(@class,'js-favorite-count')]/text()")
        if qfavorite:
            qfavorite = int(qfavorite[0])
        else:
            qfavorite = 0
        qtags = tree.xpath("//div[contains(@class,'post-taglist')]/div/a/text()")
        qtags = ', '.join(qtags)
        return [qtitle, qbody, qtimestamp, quser, qvote, qfavorite, qtags]

    def _get_comments(self, tree, qid):
        comments = tree.xpath("//div[@id='comments-"+qid+"']/ul/li/div[contains(@class,'comment-text')]/div[contains(@class,'comment-body')]")
        all_comments = []
        for cmt in comments:
            cbody = cmt.xpath(".//span[@class='comment-copy']")
            if cbody:
                cbody = cbody[0].text_content().replace('\n','<br />').replace('\r','<br />').replace('\t',' ')
            else:
                continue
            cauthor = cmt.xpath(".//a[@class='comment-user']/text()")
            if cauthor:
                cauthor = cauthor[0]
            else:
                cauthor = ""
            cdate = cmt.xpath(".//span[@class='comment-date']/span")
            if cdate:
                cdate = cdate[0].get('title')
            else:
                cdate = ''
            all_comments.append([qid,cbody,cdate,cauthor])
        return all_comments

    def _get_question_answers(self,base,tree):
        all_answers = []
        answers = tree.xpath("//div[contains(@class,'answercell')]")
        for ans in answers:
            aid = ans.xpath(".//div/div/div[@class='post-menu']/a[contains(@class,'js-share-link')]")
            if not aid:
                continue
            aurl = base + aid[0].get('href')
            aid = aid[0].get('href')[3:] # Skip /a/
            abody = ans.xpath(".//div[@class='post-text']/p/text()")
            abody = ' '.join(abody).replace('\n','<br />').replace('\r','<br />').replace('\t',' ')
            auser = ans.xpath(".//div[@class='user-details']/a/text()")
            if auser:
                auser = auser[0]
            else:
                auser = ""
            atime = ans.xpath(".//div[@class='user-action-time']/span[@class='relativetime']")
            if atime:
                atime = atime[0].get('title')
            else:
                atime = ''
            avotes = tree.xpath("//div[@data-answerid='"+aid+"']/div/div/div[contains(@class,'js-voting-container')]/div[@itemprop='upvoteCount']/text()")
            if avotes:
                avotes = avotes[0]
            else:
                avotes = '0'
            all_answers.append([aid,aurl,abody,atime,auser,avotes])
        return all_answers

    def crawl(self,dir='healthse'):
        base = 'https://medicalsciences.stackexchange.com'
        query = '/questions?pagesize=' + str(self.paging) + '&sort=newest&page='
        pages = self._get_pages(base+query+'1')

        question_urls = ""
        for i in range(1, pages+1):
            question_urls += self._get_question_links(base,query+str(i))
        question_urls = question_urls[:-1].split(',')

        counts = 0
        questions_df = pd.DataFrame(columns=['question_id','question_url','question_title','question_body','time_stamp','username','votes','favorites','tags'])
        qcomments_df = pd.DataFrame(columns=['question_id','comment','time_stamp','username'])
        answers_df = pd.DataFrame(columns=['question_id','answer_id','answer_url','answer','time_stamp','username','votes'])
        acomments_df = pd.DataFrame(columns=['question_id','answer_id','comment','time_stamp','username'])

        for qurl in question_urls:
            time.sleep(1) # Pause to avoid rate limits
            try:
                page = requests.get(qurl)
            except ConnectionError as ce:
                print ce
                time.sleep(60) # On rate limiting, pause and retry later

            counts += 1
            tree = html.soupparser.fromstring(page.content, features='html.parser')

            sep = '/questions/'
            st = qurl.find(sep)
            ed = qurl[st+len(sep):]
            qid = ed[:ed.find('/')]
            
            q = self._get_question_details(tree)
            if q is None: continue
            questions_df.loc[len(questions_df)] = [qid] + [qurl] + q
            
            qcmts = self._get_comments(tree,qid)
            for qc in qcmts:
                qcomments_df.loc[len(qcomments_df)] = qc

            qans = self._get_question_answers(base,tree)
            ans_comments = []
            for qa in qans:
                answers_df.loc[len(answers_df)] = [qid] + qa
                ans_comments.extend(self._get_comments(tree, qa[0]))

            for ac in ans_comments:
                acomments_df.loc[len(acomments_df)] = [qid] + ac

        questions_df.to_csv(path_or_buf=dir+'/questions.tsv',sep='\t',index=False,encoding='utf-8')
        qcomments_df.to_csv(path_or_buf=dir+'/question_comments.tsv',sep='\t',index=False,encoding='utf-8')
        answers_df.to_csv(path_or_buf=dir+'/answers.tsv',sep='\t',index=False,encoding='utf-8')
        acomments_df.to_csv(path_or_buf=dir+'/answer_comments.tsv',sep='\t',index=False,encoding='utf-8')
        return counts

class TestSpidey(object):
    def _get_tree(self, url):
        page = requests.get(url)
        return html.soupparser.fromstring(page.content, features='html.parser')

    def test_get_pages(self):
        assert Spidey()._get_pages('https://medicalsciences.stackexchange.com/questions?pagesize=50&sort=newest&page=1') == 120

    def test_get_question_links(self):
        assert len(Spidey()._get_question_links('https://medicalsciences.stackexchange.com','/questions?pagesize=50&sort=newest&page=1').split(',')) == 51

    def test_get_question_details1(self):
        assert Spidey()._get_question_details(self._get_tree('https://medicalsciences.stackexchange.com/questions/15473/can-diabetes-relieve-symptoms-of-hemophilia'))[5] == 0

    def test_get_question_details2(self):
        assert Spidey()._get_question_details(self._get_tree('https://medicalsciences.stackexchange.com/questions/15473/can-diabetes-relieve-symptoms-of-hemophilia'))[4] == 0
        
    def test_get_question_details3(self):
        assert Spidey()._get_question_details(self._get_tree('https://medicalsciences.stackexchange.com/questions/3585/is-eating-a-meal-with-2000-calories-at-once-any-different-from-eating-4-times-at'))[5] == 4

    def test_get_question_details4(self):
        assert Spidey()._get_question_details(self._get_tree('https://medicalsciences.stackexchange.com/questions/3585/is-eating-a-meal-with-2000-calories-at-once-any-different-from-eating-4-times-at'))[4] == 20

    def test_get_comments1(self):
        assert len(Spidey()._get_comments(self._get_tree('https://medicalsciences.stackexchange.com/questions/3585/is-eating-a-meal-with-2000-calories-at-once-any-different-from-eating-4-times-at'),'3585')) == 3

    def test_get_comments2(self):
        assert len(Spidey()._get_comments(self._get_tree('https://medicalsciences.stackexchange.com/questions/43/what-is-the-cause-of-type-1-diabetes'),'43')) == 0

    def test_get_comments3(self):
        assert Spidey()._get_comments(self._get_tree('https://medicalsciences.stackexchange.com/questions/3585/is-eating-a-meal-with-2000-calories-at-once-any-different-from-eating-4-times-at'),'3585')[1][3] == 'dakre18'

    def test_get_answer_comments1(self):
        assert len(Spidey()._get_comments(self._get_tree('https://medicalsciences.stackexchange.com/questions/3585/is-eating-a-meal-with-2000-calories-at-once-any-different-from-eating-4-times-at'),'4010')) == 0

    def test_get_answer_comments2(self):
        assert len(Spidey()._get_comments(self._get_tree('https://medicalsciences.stackexchange.com/questions/3585/is-eating-a-meal-with-2000-calories-at-once-any-different-from-eating-4-times-at'),'12521')) == 1

    def test_get_question_answers1(self):
        assert len(Spidey()._get_question_answers('https://medicalsciences.stackexchange.com',self._get_tree('https://medicalsciences.stackexchange.com/questions/3585/is-eating-a-meal-with-2000-calories-at-once-any-different-from-eating-4-times-at'))) == 2

    def test_get_question_answers2(self):
        assert Spidey()._get_question_answers('https://medicalsciences.stackexchange.com',self._get_tree('https://medicalsciences.stackexchange.com/questions/3585/is-eating-a-meal-with-2000-calories-at-once-any-different-from-eating-4-times-at'))[0][5] == '14'

    def test_get_question_answers3(self):
        assert len(Spidey()._get_question_answers('https://medicalsciences.stackexchange.com',self._get_tree('https://medicalsciences.stackexchange.com/questions/15473/can-diabetes-relieve-symptoms-of-hemophilia'))) == 0

    def test_all(self):
        self.test_get_pages()
        self.test_get_question_links()
        self.test_get_question_details1()
        self.test_get_question_details2()
        self.test_get_question_details3()
        self.test_get_question_details4()
        self.test_get_comments1()
        self.test_get_comments2()
        self.test_get_comments3()
        self.test_get_answer_comments1()
        self.test_get_answer_comments2()
        self.test_get_question_answers1()
        self.test_get_question_answers2()
        self.test_get_question_answers3()

if __name__ == '__main__':
    TestSpidey().test_all()
    Spidey().crawl()