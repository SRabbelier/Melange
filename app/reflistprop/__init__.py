#!/usr/bin/python2.5
#
# Copyright 2007 Ken Tidwell 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at 
#
#     http://www.apache.org/licenses/LICENSE-2.0 
#
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
# See the License for the specific language governing permissions and 
# limitations under the License.
# 
"""Simple property for storing ordered lists of Model objects.

It should be noted that larger lists are going to be VERY inefficient
to load (one get per object).

Currently I have no idea where that upper bound might lie, though.
 
A quick usage example:
        class Bit(db.Model):
                name = db.StringProperty(required=True)\ 
        class Holder(db.Model):
                bits = reflistprop.ReferenceListProperty(Bit, default=None) 
        b1 = Bit(name="first") 
        b1.put() # need to put it so that it is a valid reference object 
        h1 = holder() 
        h1.bits.append(b1) 
        h1.put()
         
These also work: 
        h1.bits = [b1]
         
This throws a db.BadValueError because a string is not an instance of 
Bit: 
        h1.bits = ["nasty evil string"]
         
This is not good but gets no complaint at assignment time (same 
behaviour as ListProperty)
but we will throw a db.BadValueError if you try to put it into the 
datastore. (Maybe ListProperty
wants to do the same? Or should I be waiting for the datastore 
internal entity construction to
notice the problem and throw?):
        h1.bits.append("nasty evil string")

Yes, of course you can query them. The important bit to understand is 
that the list is stored as a list of keys in the datastore. So you use 
the key of the entity in question in your query. (Seems like it would be 
nice if the property could get involved and do that coercion for you but 
I don't think it can right now...).
 
Here's a little example:
        class Thang(db.Model): 
            name = db.StringProperty(required=True) 
        class Holder(db.Model): 
            thangs = langutils.ReferenceListProperty(Thang, default=None) 
        holder1 = Holder() 
        holder1.put() 
        foo = Thang(name="foo") 
        foo.put() 
        holder1.thangs.append(foo) 
        holder1.put() 
        hq = db.GqlQuery("SELECT * FROM Holder where thangs = :1", foo.key()) 
        holders = hq.fetch(10) 
        print "Holders =", holders
        
Obtained from:
  http://groups.google.com/group/google-appengine/msg/d203cc1b93ee22d7 
"""


from google.appengine.ext import db

 
class ReferenceListProperty(db.Property):
  """A property that stores a list of models. 
  This is a parameterized property; the parameter must be a valid 
  Model type, and all items must conform to this type.
  """
  def __init__(self, item_type, verbose_name=None, default=None, **kwds): 
    """Construct ReferenceListProperty.

    Args:
      item_type: Type for the list items; must be a subclass of Model. 
      verbose_name: Optional verbose name.
      default: Optional default value; if omitted, an empty list is used. 
      **kwds: Optional additional keyword arguments, passed to base class. 
    """
    if not issubclass(item_type, db.Model): 
      raise TypeError('Item type should be a subclass of Model') 
    if default is None:
      default = []
    self.item_type = item_type 
    super(ReferenceListProperty, self).__init__(verbose_name, 
                                                default=default,
                                                **kwds)
  def validate(self, value):
    """Validate list.

    Note that validation here is just as broken as for ListProperty. 
    The values in the list are only validated if the entire list is
    swapped out.
    If the list is directly modified, there is no attempt to validate 
    the new items.

    Returns:
      A valid value. 

    Raises:
      BadValueError if property is not a list whose items are 
      instances of the item_type given to the constructor.
    """ 
    value = super(ReferenceListProperty, self).validate(value) 
    if value is not None: 
      if not isinstance(value, list): 
        raise db.BadValueError('Property %s must be a list' % 
                               self.name)
      for item in value:
        if not isinstance(item, self.item_type): 
            raise db.BadValueError(
                'Items in the %s list must all be %s instances' % 
                (self.name, self.item_type.__name__))
    return value

  def empty(self, value): 
    """Is list property empty.

    [] is not an empty value.
 
    Returns:
      True if value is None, else False. 
    """ 
    return value is None

  data_type = list
 
  def default_value(self): 
    """Default value for list.
 
    Because the property supplied to 'default' is a static value, 
    that value must be shallow copied to prevent all fields with 
    default values from sharing the same instance.
 
    Returns: 
      Copy of the default value. 
    """ 
    return list(super(ReferenceListProperty, self).default_value())
 
  def get_value_for_datastore(self, model_instance): 
    """A list of key values is stored.

    Prior to storage, we validate the items in the list. 
    This check seems to be missing from ListProperty.

    Args: 
      model_instance: Instance to fetch datastore value from.
 
    Returns: 
      A list of the keys for all Models in the value list. 
    """ 
    value = self.__get__(model_instance, model_instance.__class__) 
    self.validate(value) 
    if value is None: 
        return None 
    else: 
        return [v.key() for v in value]
 
  def make_value_from_datastore(self, value): 
    """Recreates the list of Models from the list of keys.
 
    Args:
      value: value retrieved from the datastore entity.

    Returns: 
      None or a list of Models. 
    """ 
    if value is None:
        return None
    else:
        return [db.get(v) for v in value] 
