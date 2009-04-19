#!/usr/bin/python2.5
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

"""Cron jobs.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import logging

from google.appengine.ext import db
from google.appengine.runtime import DeadlineExceededError

from soc.cron import student_proposal_mailer
from soc.models.job import Job

class Error(Exception):
  """Base class for all exceptions raised by this module.
  """
  pass


class FatalJobError(Error):
  """Class for all errors that lead to immediate job abortion.
  """
  pass


class Handler(object):
  """A handler that dispatches a cron job.

  The tasks that are mapped into tasks will be called when a worker
  has claimed the job. However, there is no guarantee as to how long
  the task will be allowed to run. If an Exception is raised the task
  is automatically rescheduled for execution.
  """

  def __init__(self):
    """Constructs a new Handler with all known jobs set.
    """

    self.OUT_OF_TIME = 0
    self.ALREADY_CLAIMED = 1
    self.SUCCESS = 2
    self.ABORTED = 3
    self.ERRORED = 4

    self.tasks = {}
    self.tasks['setupStudentProposalMailing'] = \
        student_proposal_mailer.setupStudentProposalMailing
    self.tasks['sendStudentProposalMail'] = \
        student_proposal_mailer.sendStudentProposalMail

  def claimJob(self, job_key):
    """A transaction to claim a job.
    """

    job = Job.get_by_id(job_key)

    if job.status != 'waiting':
      raise db.Rollback()

    job.status = 'started'

    if job.put():
      return job
    else:
      return None

  def freeJob(self, job_key):
    """A transaction to free a job.
    """

    job = Job.get_by_id(job_key)

    job.status = 'waiting'

    return job.put()

  def timeoutJob(self, job_key):
    """A transaction to timeout a job.
    """

    job = Job.get_by_id(job_key)

    job.timeouts += 1

    if job.timeouts > 50:
      job.status = 'aborted'
    else:
      job.status = 'waiting'

    job_id = job.key().id()
    logging.debug("job %d now timeout %d time(s)" % (job_id, job.timeouts))

    return job.put()

  def failJob(self, job_key):
    """A transaction to fail a job.
    """

    job = Job.get_by_id(job_key)

    job.errors += 1

    if job.errors > 5:
      job.status = 'aborted'
    else:
      job.status = 'waiting'

    job_id = job.key().id()
    logging.warning("job %d now failed %d time(s)" % (job_id, job.errors))

    return job.put()

  def finishJob(self, job_key):
    """A transaction to finish a job.
    """

    job = Job.get_by_id(job_key)
    job.status = 'finished'

    return job.put()

  def abortJob(self, job_key):
    """A transaction to abort a job.
    """

    job = Job.get_by_id(job_key)
    job.status = 'aborted'

    return job.put()

  def handle(self, job_key):
    """Handle one job.

    Returns: whether another job should be started after this one
    """

    try:
      job = db.run_in_transaction(self.claimJob, job_key)

      if not job:
        # someone already claimed the job
        return self.ALREADY_CLAIMED

      if job.task_name not in self.tasks:
        logging.error("Unknown job %s" % job.task_name)
        db.run_in_transaction(self.abortJob, job_key)
        return self.ABORTED

      task = self.tasks[job.task_name]

      # execute the actual job
      task(job)

      db.run_in_transaction(self.finishJob, job_key)
      return self.SUCCESS
    except DeadlineExceededError, exception:
      db.run_in_transaction(self.timeoutJob, job_key)
      return self.OUT_OF_TIME
    except FatalJobError, exception:
      logging.exception(exception)
      db.run_in_transaction(self.abortJob, job_key)
      return self.ABORTED
    except Exception, exception:
      logging.exception(exception)
      db.run_in_transaction(self.failJob, job_key)
      return self.ERRORED

  def iterate(self, jobs, retry_jobs):
    """Trivial iterator that iterates over jobs then retry_jobs
    """

    for job in jobs:
      yield job
    while retry_jobs:
      yield retry_jobs[0]

handler = Handler()
