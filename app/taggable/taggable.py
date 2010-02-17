from google.appengine.ext import db

import string
import soc.models.linkable

class Tag(db.Model):
  """Google AppEngine model for store of tags.
  """

  tag = db.StringProperty(required=True)
  "The actual string value of the tag."

  added = db.DateTimeProperty(auto_now_add=True)
  "The date and time that the tag was first added to the datastore."

  tagged = db.ListProperty(db.Key)
  "A List of db.Key values for the datastore objects that have been tagged with this tag value."

  tagged_count = db.IntegerProperty(default=0)
  "The number of entities in tagged."

  auto_delete = db.BooleanProperty(required=True, default=False)
  "If true, a tag instance should be deleted when tagged_count reaches zero."

  scope = db.ReferenceProperty(reference_class=soc.models.linkable.Linkable,
                               required=False,
                               collection_name='task_type_tags')
  "Each tag is scoped under some linkable model."

  @classmethod
  def _key_name(cls, scope_path, tag_name):
    """Create the key_name from program key_name as scope_path and tag_name.
    """

    return scope_path + '/' + tag_name

  def remove_tagged(self, key):
    def remove_tagged_txn():
      if key in self.tagged:
        self.tagged.remove(key)
        self.tagged_count -= 1
        if not self.tagged_count and self.auto_delete:
          self.delete()
        else:
          self.put()
    db.run_in_transaction(remove_tagged_txn)
    self.__class__.expire_cached_tags()

  def add_tagged(self, key):
    def add_tagged_txn():
      if key not in self.tagged:
        self.tagged.append(key)
        self.tagged_count += 1
        self.put()
    db.run_in_transaction(add_tagged_txn)
    self.__class__.expire_cached_tags()

  def clear_tagged(self):
    def clear_tagged_txn():
      if self.auto_delete:
        self.delete()
      else:
        self.tagged = []
        self.tagged_count = 0
        self.put()
    db.run_in_transaction(clear_tagged_txn)
    self.__class__.expire_cached_tags()

  @classmethod
  def get_by_name(cls, tag_name):
    """Get the list of tag objects that has the given tag_name.
    """

    tags = db.Query(cls).filter('tag =', tag_name).fetch(1000)
    return tags

  @classmethod
  def get_by_scope_and_name(cls, scope, tag_name):
    """Get a tag by scope and name.

    There may be only one such tag.
    """

    return db.Query(cls).filter(
        'scope =', scope).filter('tag =', tag_name).get()

  @classmethod
  def get_by_scope(cls, scope):
    """Get a list of tag objects that has a given scope.
    """

    return db.Query(cls).filter('scope = ', scope).fetch(1000)

  @classmethod
  def get_tags_for_key(cls, key, limit=1000):
    """Get the tags for the datastore object represented by key.
    """

    tags = db.Query(cls).filter('tagged =', key).fetch(limit)
    return tags

  @staticmethod
  def get_for_custom_query(model, filter=None, order=None, limit=1000):
    """Get a list of tag objects for a custom filter.
    """

    query = db.Query(model)

    if not filter:
      filter = {}

    for key, value in filter.iteritems():
      if isinstance(value, list) and len(value) == 1:
        value = value[0]
      if isinstance(value, list):
        op = '%s IN' % key
        query.filter(op, value)
      else:
        query.filter(key, value)

    if not order:
      order = []

    for key in order:
      filter.order(key)

    return query.fetch(limit)

  @classmethod
  def get_tags_by_frequency(cls, limit=1000):
    """Return a list of Tags sorted by the number of objects to which they
    have been applied, most frequently-used first. If limit is given, return
    only return only that many tags; otherwise, return all.
    """

    tag_list = db.Query(cls).filter('tagged_count >', 0).order(
        "-tagged_count").fetch(limit)

    return tag_list

  @classmethod
  def get_tags_by_name(cls, limit=1000, ascending=True):
    """Return a list of Tags sorted alphabetically by the name of the tag.
    If a limit is given, return only that many tags; otherwise, return all.
    If ascending is True, sort from a-z; otherwise, sort from z-a.
    """

    from google.appengine.api import memcache

    cache_name = cls.__name__ + '_tags_by_name'
    if ascending:
      cache_name += '_asc'
    else:
      cache_name += '_desc'

    tags = memcache.get(cache_name)
    if tags is None or len(tags) < limit:
      order_by = "tag"
      if not ascending:
        order_by = "-tag"

      tags = db.Query(cls).order(order_by).fetch(limit)
      memcache.add(cache_name, tags, 3600)
    else:
      if len(tags) > limit:
        # Return only as many as requested.
        tags = tags[:limit]

    return tags

  @classmethod
  def get_or_create(cls, scope, tag_name):
    """Get the Tag object that has the tag value given by tag_value.
    """

    tag_key_name = cls._key_name(scope.key().name(), tag_name)
    existing_tag = cls.get_by_key_name(tag_key_name)
    if existing_tag is None:
      # the tag does not yet exist, so create it.
      def create_tag_txn():
        new_tag = cls(key_name=tag_key_name, tag=tag_name, scope=scope)
        new_tag.put()
        return new_tag
      existing_tag = db.run_in_transaction(create_tag_txn)
    return existing_tag

  @classmethod
  def copy_tag(cls, scope, tag_name, new_tag_name):
    """Copy a tag with a given scope and tag_name to another tag with
    new tag_name.
    """
    tag = cls.get_by_scope_and_name(scope, tag_name)

    if tag:
      tag_key_name = cls._key_name(scope.key().name(), new_tag_name)
      existing_tag = cls.get_by_key_name(tag_key_name)

      if existing_tag is None:
        new_tag = cls(key_name=tag_key_name, tag=new_tag_name, scope=scope, 
                      added=tag.added, tagged=tag.tagged,
                      tagged_count=tag.tagged_count)
        new_tag.put()
        tag.delete()

        return new_tag

      return existing_tag

    return None

  @classmethod
  def delete_tag(cls, scope, tag_name):
    """Delete a tag with a given scope and tag_name.
    """

    tag = cls.get_by_scope_and_name(scope, tag_name)

    if tag:
      tag.delete()
      return True

    return False

  @classmethod
  def popular_tags(cls, limit=5):
    """Get the most popular tags from memcache, or if they are not defined
    there, it retrieves them from datastore and sets in memcache.
    """

    from google.appengine.api import memcache

    tags = memcache.get(cls.__name__ + '_popular_tags')
    if tags is None:
      tags = cls.get_tags_by_frequency(limit)
      memcache.add(cls.__name__ + '_popular_tags', tags, 3600)

    return tags

  @classmethod
  def expire_cached_tags(cls):
    """Expire all tag lists which exist in memcache.
    """

    from google.appengine.api import memcache

    memcache.delete(cls.__name__ + '_popular_tags')
    memcache.delete(cls.__name__ + '_tags_by_name_asc')
    memcache.delete(cls.__name__ + '_tags_by_name_desc')

  def __str__(self):
    """Returns the string representation of the entity's tag name.
    """

    return self.tag


def tag_property(tag_name):
  """Decorator that creates and returns a tag property to be used
  in Google AppEngine model.

  Args:
    tag_name: name of the tag to be created.
  """

  def get_tags(self):
    """"Get a list of Tag objects for all Tags that apply to the
    specified entity.
    """

    if self._tags[tag_name] is None or len(self._tags[tag_name]) == 0:
      self._tags[tag_name] = self._tag_model[
          tag_name].get_tags_for_key(self.key())
    return self._tags[tag_name]

  def set_tags(self, seed):
    """Set a list of Tag objects for all Tags that apply to
    the specified entity.
    """

    import types
    if type(seed['tags']) is types.UnicodeType:
      # Convert unicode to a plain string
      seed['tags'] = str(seed['tags'])
    if type(seed['tags']) is types.StringType:
      # Tags is a string, split it on tag_seperator into a list
      seed['tags'] = string.split(seed['tags'], self.tag_separator)
    if type(seed['tags']) is types.ListType:
      get_tags(self)
      # Firstly, we will check to see if any tags have been removed.
      # Iterate over a copy of _tags, as we may need to modify _tags
      for each_tag in self._tags[tag_name][:]:
        if each_tag not in seed['tags']:
          # A tag that was previously assigned to this entity is
          # missing in the list that is being assigned, so we
          # disassocaite this entity and the tag.
          each_tag.remove_tagged(self.key())
          self._tags[tag_name].remove(each_tag)
      # Secondly, we will check to see if any tags have been added.
      for each_tag in seed['tags']:
        each_tag = string.strip(each_tag)
        if len(each_tag) > 0 and each_tag not in self._tags[tag_name]:
          # A tag that was not previously assigned to this entity
          # is present in the list that is being assigned, so we
          # associate this entity with the tag.
          tag = self._tag_model[tag_name].get_or_create(
              seed['scope'], each_tag)
          tag.add_tagged(self.key())
          self._tags[tag_name].append(tag)
    else:
      raise Exception, "tags must be either a unicode, a string or a list"

  return property(get_tags, set_tags)


class Taggable(object):
  """A mixin class that is used for making GAE Model classes taggable.

  This is an extended version of Taggable-mixin which allows for
  multiple tag properties in the same AppEngine Model class.
  """

  def __init__(self, **kwargs):
    """The constructor class for Taggable, that creates a dictionary of tags.

    The difference from the original taggable in terms of interface is
    that, tag class is not used as the default tag model, since we don't
    have a default tag property created in this class now.

    Args:
      kwargs: keywords containing the name of the tags and arguments
          containing tag model to be used.
    """

    self._tags = {}
    self._tag_model = {}

    for tag_name in kwargs:
      self._tags[tag_name] = None
      self._tag_model[tag_name] = kwargs[tag_name]

    self.tag_separator = ", "

  def tags_string(self, tag_name, ret_list=False):
    """Create a formatted string version of this entity's tags.

    Args:
      tag_name: the name of the tag which must be formatted
      ret_list: if False sends a string, otherwise sends a Python list
    """

    tag_list = [each_tag.tag for each_tag in tag_name]

    if ret_list:
      return tag_list
    else:
      return self.tag_separator.join(tag_list)

  def tags_class(self, tag_name):
    """Return a class instance object for a given tag name.
    """

    return self._tag_model[tag_name]
