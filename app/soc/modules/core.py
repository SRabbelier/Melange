# Copyright 2009 the Melange authors.
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

"""The Melange Core module.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django.conf.urls import defaults

import settings
import soc.cache.sidebar


class Error(Exception):
  """Error class for the callback module.
  """

  pass


class APIVersionMismatch(Error):
  """Error raised when API version mismatches.
  """

  MISMATCH_MSG_FMT = "API mismatch, expected '%d', got '%d'."

  def __init__(self, expected, actual):
    """Instantiates a new exception with a customized message.
    """

    msg = self.MISMATCH_MSG_FMT % (expected, actual)
    super(APIVersionMismatch, self).__init__(msg)


class MissingService(Error):
  """Error raised when a required service is missing.
  """

  MISSING_SERVICE_FMT = "Required service '%s' is not registered, known: %s"

  def __init__(self, service, services):
    """Instantiates a new exception with a customized message.
    """

    msg = self.MISSING_SERVICE_FMT % (service, services)
    super(MissingService, self).__init__(msg)


class MissingCapability(Error):
  """Error raised when a required capability is missing.
  """

  MISSING_CAPABILITY_FMT = "Required capability '%s' " + \
      "is not registered, known: %s"

  def __init__(self, capability, capabilities):
    """Instantiates a new exception with a customized message.
    """

    msg = self.MISSING_CAPABILITY_FMT % (capability, capabilities)
    super(MissingCapability, self).__init__(msg)


class NonUniqueService(Error):
  """Error raised when a required service is missing.
  """

  NON_UNIQUE_SERVICE_FMT = "Unique service '%s' called a 2nd time, known: %s."

  def __init__(self, service, services):
    """Instantiates a new exception with a customized message.
    """

    msg = self.NON_UNIQUE_SERVICE_FMT % (service, services)
    super(NonUniqueService, self).__init__(msg)


class Core(object):
  """The core handler that controls the Melange API.
  """

  def __init__(self):
    """Creates a new instance of the Core.
    """
    
    # pylint: disable-msg=C0103
    self.API_VERSION = 1

    self.registered_callbacks = []
    self.capabilities = []
    self.services = []

    self.sitemap = []
    self.sidebar = []

  ##
  ## internal
  ##

  def getService(self, callback, service):
    """Retrieves the specified service from the callback if supported.

    Args:
     callback: the callback to retrieve the capability from
     service: the service to retrieve
    """

    if not hasattr(callback, service):
      return False

    func = getattr(callback, service)

    if not callable(func):
      return False

    return func

  ##
  ## Core code
  ##

  def getPatterns(self):
    """Returns the Django patterns for this site.
    """

    self.callService('registerWithSitemap', True)
    return defaults.patterns(None, *self.sitemap)

  @soc.cache.sidebar.cache
  def getSidebar(self, id, user):
    """Constructs a sidebar for the current user.
    """

    self.callService('registerWithSidebar', True)

    sidebar = []

    for i in self.sidebar:
      menus = i(id, user)

      for menu in (menus if menus else []):
        sidebar.append(menu)

    return sorted(sidebar, key=lambda x: x.get('group'))

  def callService(self, service, unique, *args, **kwargs):
    """Calls the specified service on all callbacks.
    """

    if unique and (service in self.services):
      return

    results = []

    for callback in self.registered_callbacks:
      func = self.getService(callback, service)
      if not func:
        continue

      result = func(*args, **kwargs)
      results.append(result)

    self.services.append(service)
    return results

  def registerModuleCallbacks(self):
    """Retrieves all callbacks for the modules of this site.

    Callbacks for modules without a version number or the wrong API_VERSION
    number are dropped.  They won't be called.
    """

    fmt = settings.MODULE_FMT
    modules = ['soc_core'] + settings.MODULES
    modules = [__import__(fmt % i, fromlist=['']) for i in modules]

    for callback_class in [i.Callback for i in modules]:
      if callback_class.API_VERSION != self.API_VERSION:
        raise APIVersionMismatch(self.API_VERSION,
                                 callback_class.API_VERSION)


      callback = callback_class(self)
      self.registered_callbacks.append(callback)

    return True

  ##
  ## Module code
  ##

  def registerCapability(self, capability):
    """Registers the specified capability.
    """

    self.capabilities.append(capability)

  def requireCapability(self, capability):
    """Requires that the specified capability is present.
    """

    if capability in self.capabilities:
      return True

    raise MissingCapability(capability, self.capabilities)

  def requireService(self, service):
    """Requires that the specified service has been called.
    """

    if service in self.services:
      return True

    raise MissingService(service, self.services)

  def requireUniqueService(self, service):
    """Requires that the specified service is called exactly once.
    """

    if service not in self.services:
      return True

    raise NonUniqueService(service, self.services)

  def registerSitemapEntry(self, entries):
    """Registers the specified entries with the sitemap.
    """

    self.sitemap.extend(entries)

  def registerSidebarEntry(self, entry):
    """Registers the specified entry with the sidebar.
    """

    self.sidebar.append(entry)
