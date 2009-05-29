from google.appengine.ext import db
import string
    
class Tag(db.Model):
    "Google AppEngine model for store of tags."
    
    tag = db.StringProperty(required=True)
    "The actual string value of the tag."
    
    added = db.DateTimeProperty(auto_now_add=True)
    "The date and time that the tag was first added to the datastore."
    
    tagged = db.ListProperty(db.Key)
    "A List of db.Key values for the datastore objects that have been tagged with this tag value."
    
    tagged_count = db.IntegerProperty(default=0)
    "The number of entities in tagged."

    @staticmethod
    def __key_name(tag_name):
        return "tag_%s" % tag_name
    
    def remove_tagged(self, key):
        def remove_tagged_txn():
            if key in self.tagged:
                self.tagged.remove(key)
                self.tagged_count -= 1
                self.put()
        db.run_in_transaction(remove_tagged_txn)
        Tag.expire_cached_tags()

    def add_tagged(self, key):
        def add_tagged_txn():
            if key not in self.tagged:
                self.tagged.append(key)
                self.tagged_count += 1
                self.put()
        db.run_in_transaction(add_tagged_txn)
        Tag.expire_cached_tags()
    
    def clear_tagged(self):
        def clear_tagged_txn():
            self.tagged = []
            self.tagged_count = 0
            self.put()
        db.run_in_transaction(clear_tagged_txn)
        Tag.expire_cached_tags()
        
    @classmethod
    def get_by_name(cls, tag_name):
        return Tag.get_by_key_name(Tag.__key_name(tag_name))
    
    @classmethod
    def get_tags_for_key(cls, key):
        "Set the tags for the datastore object represented by key."
        tags = db.Query(Tag).filter('tagged =', key).fetch(1000)
        return tags
    
    @classmethod
    def get_or_create(cls, tag_name):
        "Get the Tag object that has the tag value given by tag_value."
        tag_key_name = Tag.__key_name(tag_name)
        existing_tag = Tag.get_by_key_name(tag_key_name)
        if existing_tag is None:
            # The tag does not yet exist, so create it.
            def create_tag_txn():
                new_tag = Tag(key_name=tag_key_name, tag = tag_name)
                new_tag.put()
                return new_tag
            existing_tag = db.run_in_transaction(create_tag_txn)
        return existing_tag
    
    @classmethod
    def get_tags_by_frequency(cls, limit=1000):
        """Return a list of Tags sorted by the number of objects to which they have been applied,
        most frequently-used first.  If limit is given, return only that many tags; otherwise,
        return all."""
        tag_list = db.Query(Tag).filter('tagged_count >', 0).order("-tagged_count").fetch(limit)
            
        return tag_list

    @classmethod
    def get_tags_by_name(cls, limit=1000, ascending=True):
        """Return a list of Tags sorted alphabetically by the name of the tag.
        If a limit is given, return only that many tags; otherwise, return all.
        If ascending is True, sort from a-z; otherwise, sort from z-a."""

        from google.appengine.api import memcache

        cache_name = 'tags_by_name'
        if ascending:
            cache_name += '_asc'
        else:
            cache_name += '_desc'
            
        tags = memcache.get(cache_name)
        if tags is None or len(tags) < limit:
            order_by = "tag"
            if not ascending:
                order_by = "-tag"
            
            tags = db.Query(Tag).order(order_by).fetch(limit)
            memcache.add(cache_name, tags, 3600)
        else:
            if len(tags) > limit:
                # Return only as many as requested.
                tags = tags[:limit]
                
        return tags
        
    
    @classmethod
    def popular_tags(cls, limit=5):
        from google.appengine.api import memcache
        
        tags = memcache.get('popular_tags')
        if tags is None:
            tags = Tag.get_tags_by_frequency(limit)
            memcache.add('popular_tags', tags, 3600)
        
        return tags

    @classmethod
    def expire_cached_tags(cls):
        from google.appengine.api import memcache
        
        memcache.delete('popular_tags')
        memcache.delete('tags_by_name_asc')
        memcache.delete('tags_by_name_desc')

class Taggable:
    """A mixin class that is used for making Google AppEnigne Model classes taggable.
        Usage:
            class Post(db.Model, taggable.Taggable):
                body = db.TextProperty(required = True)
                title = db.StringProperty()
                added = db.DateTimeProperty(auto_now_add=True)
                edited = db.DateTimeProperty()
            
                def __init__(self, parent=None, key_name=None, app=None, **entity_values):
                    db.Model.__init__(self, parent, key_name, app, **entity_values)
                    taggable.Taggable.__init__(self)
    """
    
    def __init__(self):
        self.__tags = None
        self.tag_separator = ","
        """The string that is used to separate individual tags in a string
        representation of a list of tags.  Used by tags_string() to join the tags
        into a string representation and tags setter to split a string into
        individual tags."""

    def __get_tags(self):
        "Get a List of Tag objects for all Tags that apply to this object."
        if self.__tags is None or len(self.__tags) == 0:
            self.__tags = Tag.get_tags_for_key(self.key())
        return self.__tags

    def __set_tags(self, tags):
        import types
        if type(tags) is types.UnicodeType:
            # Convert unicode to a plain string
            tags = str(tags)
        if type(tags) is types.StringType:
            # Tags is a string, split it on tag_seperator into a list
            tags = string.split(tags, self.tag_separator)
        if type(tags) is types.ListType:
            self.__get_tags()
            # Firstly, we will check to see if any tags have been removed.
            # Iterate over a copy of __tags, as we may need to modify __tags
            for each_tag in self.__tags[:]:
                if each_tag not in tags:
                    # A tag that was previously assigned to this entity is
                    # missing in the list that is being assigned, so we
                    # disassocaite this entity and the tag.
                    each_tag.remove_tagged(self.key())
                    self.__tags.remove(each_tag)
            # Secondly, we will check to see if any tags have been added.
            for each_tag in tags:
                each_tag = string.strip(each_tag)
                if len(each_tag) > 0 and each_tag not in self.__tags:
                    # A tag that was not previously assigned to this entity
                    # is present in the list that is being assigned, so we
                    # associate this entity with the tag.
                    tag = Tag.get_or_create(each_tag)
                    tag.add_tagged(self.key())
                    self.__tags.append(tag)
        else:
            raise Exception, "tags must be either a unicode, a string or a list"
        
    tags = property(__get_tags, __set_tags, None, None)
    
    def tags_string(self):
        "Create a formatted string version of this entity's tags"
        to_str = ""
        for each_tag in self.tags:
            to_str += each_tag.tag
            if each_tag != self.tags[-1]:
                to_str += self.tag_separator
        return to_str
    
