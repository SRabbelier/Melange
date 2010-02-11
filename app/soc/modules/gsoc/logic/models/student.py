#!/usr/bin/env python2.5
#
# Copyright 2009 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""GSoCStudent (Model) query functions.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import student

import soc.models.student

from soc.modules.gsoc.logic.models import program as program_logic

import soc.modules.gsoc.models.student


class Logic(student.Logic):
  """Logic methods for the GSoCStudent model.
  """

  def __init__(self, model=soc.modules.gsoc.models.student.GSoCStudent,
               base_model=soc.models.student.Student,
               scope_logic=program_logic, role_name='gsoc_student'):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic,
                                role_name=role_name)


logic = Logic()
