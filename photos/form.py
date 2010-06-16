from formencode import Schema, validators, ForEach

class AlbumForm(Schema):
        author = validators.UnicodeString(not_empty=True)
        name = validators.UnicodeString(not_empty=True)
        picture = ForEach(validators.Int())

class CommentForm(Schema):
        username = validators.UnicodeString(not_empty=True)
        content = validators.UnicodeString(not_empty=True)
