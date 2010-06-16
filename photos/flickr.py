import ConfigParser
import flickrapi

config = ConfigParser.ConfigParser()
config.read('config.ini')
api_key = config.get('flickr', 'key').strip("'")
group_id = config.get('flickr', 'group').strip("'")

flickr = flickrapi.FlickrAPI(api_key)

def get_new(min_taken_date=None):
	page = 1
	def pictures(page):
		return flickr.photos_search(
				group_id=group_id, 
				per_page=500, 
				page=page, 
				extras='date_taken,owner_name',
				min_taken_date=min_taken_date)
	def picture(sets):
		return sets.find('photos').findall('photo')
	sets = pictures(page)
	photos = []
	while int(sets.find('photos').attrib['pages']) >= page and picture(sets) is not None:
		photos.extend(picture(sets))
		page += 1
		sets = pictures(page)
	return photos

def get_tags(picture):
	def tags():
		return flickr.tags_getListPhoto(
				photo_id=picture
				)
	
	def tag(tags):
		return tags.find('photo').find('tags').findall('tag')
	return [tag.__dict__ for tag in tag(tags())]
