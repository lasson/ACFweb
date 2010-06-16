import cherrypy
import os
import flickr
from formencode import Invalid
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from model import Base, Album, Picture
from form import AlbumForm
from lib import template

min_date_taken = None

def connect(thread_index):
	engine = create_engine(cherrypy.tree.apps[''].config['database']['url'])
	Session = sessionmaker(bind=engine)
	Base.metadata.create_all(engine)
	session = Session()
        picture = session.query(Picture).order_by(Picture.datetaken.desc()).first()
	if picture:
		min_date_taken = picture.datetaken.replace(
				day=picture.datetaken.day+1
				).strftime(
						"%Y-%m-%d"
						)
	pictures = flickr.get_new(min_date_taken)
	if pictures:
		for picture in pictures:
			picture = Picture(picture.attrib)
			session.merge(picture)
        session.commit()
	session.close()

	cherrypy.thread_data.db = Session()

cherrypy.engine.subscribe('start_thread', connect)

class Photos:
	@cherrypy.expose
	@template.output('photos/index.html')
	def index(self):
		session = cherrypy.thread_data.db
		albums = session.query(Album).all()
		return template.render(albums=albums)

	@cherrypy.expose
	@template.output('photos/submit.html')
	def submit(self, cancel=False, **data):
		session = cherrypy.thread_data.db
		if cherrypy.request.method == 'POST':
			if cancel:
				raise cherrypy.HTTPRedirect('/')
			form = AlbumForm()
			try:
				data = form.to_python(data)
				pictures = session.query(Picture).filter(Picture.id.in_(data['picture'])).all()
				album = Album(
						data['author'],
						data['name'],
						pictures
						)
				session.add(album)
				session.commit()
				raise cherrypy.HTTPRedirect('/')
			except Invalid, e:
				errors = e.unpack_errors()
		else:
			errors = {}
		pictures = session.query(Picture).all()
		return template.render(pictures=pictures, errors=errors)

	@cherrypy.expose
	@template.output('photos/album.html')
	def album(self, name):
		session = cherrypy.thread_data.db
		album = session.query(Album).filter_by(name=name).first()
		return template.render(album=album)

	@cherrypy.expose
	@template.output('photos/picture.html')
	def picture(self, picture):
		session = cherrypy.thread_data.db
		picture = session.query(Picture).filter_by(id=int(picture)).first()
		return template.render(picture=picture)

cherrypy.quickstart(Photos(), '/', 'config.ini')
