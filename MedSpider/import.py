import pandas as pd, pickle
import mysql.connector as mariadb

mdb = mariadb.connect(user='root', password='', database='cardea_db')
mdbc = mdb.cursor()

class Core:
	def __init__(self, admin_id:int, source_id:int, forum:str, visibility:str, identity:str, role:str):
		self.admin_id = admin_id
		self.source_id = source_id
		self.forum = forum
		self.visibility = visibility
		self.identity = identity
		self.role = role
		self.topics = []
		self.users = []

	def import_users(self, input_file:str):
		mdbc.execute("DELETE FROM users WHERE source_id = %s" % (self.source_id,)) # Clear old data

		discussions = pd.read_csv(input_file, delimiter='\t', na_filter=False)
		users = discussions['user_name'].unique()
		qry = "INSERT INTO users (email, display_name, role, source_id) VALUES (%s, %s, %s, %s)"
		for user in users:
			data = (user, user, self.role, self.source_id)
			mdbc.execute(qry, data)
			mdb.commit()
			new_id = mdbc.lastrowid
			self.users.append((user, new_id))

	def import_topics(self, input_file:str):
		type_of = 'group'
		topics = pd.read_csv(input_file, delimiter='\t', na_filter=False)
		mdbc.execute("DELETE FROM posts WHERE source_id = %s" % (self.source_id,)) # Clear old data

		qry = "INSERT INTO posts (user_id, source_id, forum, type_of, visibility, identity, title, content) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
		for row in topics.itertuples():
			id = row.id
			title = row.title
			desc = row.description
			parent = row.parent_id
			if parent == '': continue
			data = (self.admin_id, self.source_id, self.forum, type_of, self.visibility, self.identity, title, desc)
			mdbc.execute(qry, data)
			mdb.commit()
			new_id = mdbc.lastrowid
			self.topics.append((id, new_id))

	def import_discussions(self):
		pass

	def import_blogs(self):
		pass

	def import_questions(self):
		pass

	def topics_lookup(self, id:int):
		for row in self.topics:
			if row[0] == id:
				return row[1]
		return None

	def users_lookup(self, id:str):
		for row in self.users:
			if row[0] == id:
				return row[1]
		return None

class Doc2Doc(Core):
	def __init__(self, admin_id:int, source_id:int):
		Core.__init__(self, admin_id=admin_id, source_id=source_id, forum='m2m', visibility='public', identity='self', role='medic')

	def import_discussions(self):
		discussions = pd.read_csv('doc2doc/discussions.tsv', delimiter='\t', na_filter=False)
		discussion_threads = discussions['thread_id'].unique()
		threads = pd.read_csv('doc2doc/threads.tsv', delimiter='\t', na_filter=False)

		qry = "INSERT INTO posts (parent_id, user_id, source_id, forum, type_of, visibility, identity, content, time_stamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

		for thread_id in discussion_threads:
			type_of = 'discussion'
			discussion = discussions[discussions['thread_id'] == thread_id].sort_values(by='last_updated')
			topic_id = threads[threads['id'] == thread_id]['topic_id'].tolist()[0]
			parent = self.topics_lookup(topic_id)
			if parent is None: continue

			first = True
			for row in discussion.itertuples():
				desc = row.body
				time_stamp = row.last_updated
				user_id = self.users_lookup(row.user_name)
				if user_id is None: continue
				
				data = (parent, user_id, self.source_id, self.forum, type_of, self.visibility, self.identity, desc, time_stamp)
				mdbc.execute(qry, data)
				mdb.commit()
				new_id = mdbc.lastrowid

				if first:
					first = False
					parent = new_id
					type_of = 'comment'

class DocCheck(Core):
	def __init__(self, admin_id:int, source_id:int):
		Core.__init__(self, admin_id=admin_id, source_id=source_id, forum='m2m', visibility='public', identity='self', role='medic')

	def import_users(self):
		super().import_users('doccheck/blogs.tsv')
		super().import_users('doccheck/comments.tsv')

	def import_blogs(self):
		blogs = pd.read_csv('doccheck/blogs.tsv', delimiter='\t', na_filter=False)
		all_comments = pd.read_csv('doccheck/comments.tsv', delimiter='\t', na_filter=False)
		qry = "INSERT INTO posts (parent_id, user_id, source_id, forum, type_of, visibility, identity, title, content, time_stamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		
		for row in blogs.itertuples():
			type_of = 'blog'
			id = row.id
			parent = self.topics_lookup(row.topic_id)
			title = row.title
			desc = row.body
			time_stamp = row.last_updated
			user_id = self.users_lookup(row.user_name)
			if user_id is None: continue

			data = (parent, user_id, self.source_id, self.forum, type_of, self.visibility, self.identity, title, desc, time_stamp)
			mdbc.execute(qry, data)
			mdb.commit()
			new_id = mdbc.lastrowid

			comments = all_comments[all_comments['blog_id'] == id]
			
			c_qry = "INSERT INTO posts (parent_id, user_id, source_id, forum, type_of, visibility, identity, content, time_stamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
			type_of = 'comment'
			for row in comments.itertuples():
				c_desc = row.body
				c_time_stamp = row.last_updated
				c_user_id = self.users_lookup(row.user_name)
				if c_user_id is None: continue

				c_data = (new_id, c_user_id, self.source_id, self.forum, type_of, self.visibility, self.identity, c_desc, c_time_stamp)
				mdbc.execute(c_qry, c_data)
				mdb.commit()

class DoctorsLounge(Core):
	def __init__(self, admin_id:int, source_id:int, sample_size:int=100):
		Core.__init__(self, admin_id=admin_id, source_id=source_id, forum='p2m', visibility='public', identity='self', role=None)
		self.sample_size = sample_size

	def import_users_topics(self):
		mdbc.execute("DELETE FROM users WHERE source_id = %s" % (self.source_id,)) # Clear old data
		mdbc.execute("DELETE FROM posts WHERE source_id = %s" % (self.source_id,)) # Clear old data

		discussions = pd.read_csv('doctorslounge/discussions.tsv', delimiter='\t', na_filter=False, encoding='ISO-8859-1')[:self.sample_size]
		users_qry = "INSERT INTO users (email, display_name, role, source_id) VALUES (%s, %s, %s, %s)"
		topics_qry = "INSERT INTO posts (user_id, source_id, forum, type_of, visibility, identity, title) VALUES (%s, %s, %s, %s, %s, %s, %s)"
		
		user_names = []
		topic_titles = []
		for row in discussions.itertuples():
			user_name = row.username
			if user_name not in user_names:
				user_names.append(user_name)
				role = 'medic' if row.is_medic else 'patient'
				user_data = (user_name, user_name, role, self.source_id)
				mdbc.execute(users_qry, user_data)
				mdb.commit()
				new_user_id = mdbc.lastrowid
				self.users.append((user_name, new_user_id))

			topic_title = row.forum_name
			if topic_title not in topic_titles: 
				topic_titles.append(topic_title)
				topic_id = row.forum_id
				topic_data = (self.admin_id, self.source_id, self.forum, 'group', self.visibility, self.identity, topic_title)
				mdbc.execute(topics_qry, topic_data)
				mdb.commit()
				new_topic_id = mdbc.lastrowid
				self.topics.append((topic_id, new_topic_id))

	def import_questions(self):
		discussions = pd.read_csv('doctorslounge/discussions.tsv', delimiter='\t', na_filter=False, encoding='ISO-8859-1')[:self.sample_size]
		discussion_threads = discussions['discussion_id'].unique()

		qry = "INSERT INTO posts (parent_id, user_id, source_id, forum, type_of, visibility, identity, title, content, time_stamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

		for thread_id in discussion_threads:
			type_of = 'question'
			discussion = discussions[discussions['discussion_id'] == thread_id].sort_values(by='posted_date')
			topic_id = discussions[discussions['discussion_id'] == thread_id]['forum_id'].tolist()[0]
			parent = self.topics_lookup(topic_id)
			if parent is None: continue

			first = True
			for row in discussion.itertuples():
				title = row.discussion_title
				desc = row.content
				time_stamp = row.posted_date
				user_id = self.users_lookup(row.username)
				if user_id is None: continue
				
				data = (parent, user_id, self.source_id, self.forum, type_of, self.visibility, self.identity, title, desc, time_stamp)
				mdbc.execute(qry, data)
				mdb.commit()
				new_id = mdbc.lastrowid

				if first:
					first = False
					parent = new_id
					type_of = 'comment'

class eHealthForum(Core):
	def __init__(self, admin_id:int, source_id:int, sample_size:int=100):
		Core.__init__(self, admin_id=admin_id, source_id=source_id, forum='p2m', visibility='public', identity='self', role=None)
		self.sample_size = sample_size

	def import_chats(self):
		chats = pd.read_csv('ehealthforum/chats.tsv', delimiter='\t', na_filter=False)
		chat_threads = chats['discussion_id'].unique()
		
		qry = "INSERT INTO posts (parent_id, user_id, source_id, forum, type_of, visibility, identity, content, time_stamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

		for thread_id in chat_threads:
			type_of = 'chat'
			chat = chats[chats['discussion_id'] == thread_id].sort_values(by='posted_date')
			topic_id = chat['forum_id'].tolist()[0]
			parent = self.topics_lookup(topic_id)
			if parent is None: continue

			first = True
			#forum_id	forum_name	discussion_id	discussion_title	discussion_url	post_id	posted_date	user_name	content
			for row in chat.itertuples():
				desc = row.content
				time_stamp = row.posted_date
				user_id = self.users_lookup(row.user_name)
				if user_id is None: continue
				
				data = (parent, user_id, self.source_id, self.forum, type_of, self.visibility, self.identity, desc, time_stamp)
				mdbc.execute(qry, data)
				mdb.commit()
				new_id = mdbc.lastrowid

				if first:
					first = False
					parent = new_id
					type_of = 'comment'

def run_doc2doc():
	doc2doc = Doc2Doc(admin_id=1, source_id=1)
	doc2doc.import_users('doc2doc/discussions.tsv')
	doc2doc.import_topics('doc2doc/topics.tsv')
	doc2doc.import_discussions()

def run_doccheck():
	doccheck = DocCheck(admin_id=1, source_id=2)
	doccheck.import_users()
	doccheck.import_topics('doccheck/topics.tsv')
	doccheck.import_blogs()

def run_doctorslounge():
	doclounge = DoctorsLounge(admin_id=1, source_id=3)
	doclounge.import_users_topics()
	doclounge.import_questions()

def run_healthforum():
	ehealth = eHealthForum(admin_id=1, source_id=4)
	ehealth.import_users('ehealthforum/chats.tsv')

if __name__ == "__main__":
	run_doc2doc()
	run_doccheck()
	run_doctorslounge()