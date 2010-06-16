##
## Copyright 2010  Josh Lasson josh.lasson@gmail.com
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions
## are met:
## 
## 1. Redistributions of source code must retain the above copyright
##    notice, this list of conditions and the following disclaimer.
## 2. Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
## 
## THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
## IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
## OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
## IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
## INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
## NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
## THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
## 

import string
import flickr
from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Content(Base):
	__tablename__ = 'content'

	id = Column(Integer, primary_key=True)
	type = Column(String, primary_key=True)

	__mapper_args__ = {'polymorphic_on': type}
	comments = relationship(
			'Comment',
			order_by='Comment.date',
			backref='content'
			)
	tags = relationship(
			'Tag',
			secondary='content_tags',
			order_by='Tag.text',
			backref='contents'
			)

class Picture(Content):
	__tablename__ = 'picture'
	__mapper_args__ = {'polymorphic_identity': 'picture'}

	id = Column(Integer, ForeignKey('content.id'), primary_key=True)
	server = Column(Integer, nullable=False)
	farm = Column(Integer, nullable=False)
	secret = Column(String, nullable=False)
	owner = Column(String, nullable=False)
	title = Column(String, nullable=False)
	ownername = Column(String, nullable=False)
	datetaken = Column(DateTime, nullable=False)

	def __init__(self, picture):
		for key in picture.keys():
			if key == 'datetaken':
				self.date_taken = datetime.strptime(
						picture[key],
						"%Y-%m-%d %H:%M:%S"
						)
			elif hasattr(self, key):
				setattr(self, key, picture[key])
		tags = flickr.get_tags(self.id)
		for tag in tags:
			tag = Tag(tag)
			self.tags.append(tag)
	
	def __repr__(self):
		return "<Picture('%s', '%s', '%s', '%s')>" % (
				self.id,
				self.server,
				self.farm,
				self.secret
				)

	def url(self):
		return 'http://farm%s.static.flickr.com/%s/%s_%s.jpg' % (
				self.farm,
				self.server,
				self.id,
				self.secret
				)

class Album(Content):
	__tablename__ = 'album'
	__mapper_args__ = {'polymorphic_identity': 'album'}

	id = Column(Integer, ForeignKey('content.id'),  primary_key=True)
	name = Column(String, unique=True, nullable=False)
	author = Column(String, nullable=False)

	pictures = relationship(
			'Picture', 
			secondary='album_pictures', 
			backref='albums'
			)

	def __init__(self, author, name, pictures=None):
		self.name = name
                self.author = author
		if pictures:
			self.pictures.extend(pictures)
	
	def __repr__(self):
		return "<Album('%s')>" % self.name

class Comment(Base):
	__tablename__ = 'comment'

	content_id = Column(Integer, ForeignKey('content.id'), primary_key=True)
	author = Column(String, primary_key=True)
	date = Column(DateTime, default=func.now(), primary_key=True)
	text = Column(String)

	def __init__(self, author, text):
		self.author = author
		self.text = text
	
	def __repr__(self):
		return "<Comment('%s', '%s', '%s')>" % (
				self.content_id,
				self.author,
				self.date
				)
	
	def __str__(self):
		return self.text

class Tag(Base):
	__tablename__ = 'tag'

	text = Column(String, primary_key=True)

	def __init__(self, tag):
		for key in tag.keys():
			if hasattr(self, key):
				setattr(self, key, tag[key])
	
	def __repr__(self):
		return "<Tag('%s')>" % self.text

	def __str__(self):
		return self.text

content_tags = Table('content_tags', Base.metadata,
		Column('content_id', Integer, ForeignKey('content.id')),
		Column('tag_id', String, ForeignKey('tag.text'))
		)

album_pictures = Table('album_pictures', Base.metadata,
		Column('album_id', Integer, ForeignKey('album.id')),
		Column('picture_id', Integer, ForeignKey('picture.id'))
		)
