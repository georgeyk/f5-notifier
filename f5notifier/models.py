# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2012 - George Y. Kussumoto <georgeyk.dev@gmail.com>
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
##

import datetime
import hashlib
import urllib2
import random

from gi.repository import GObject, GLib

from f5notifier.notification import send_message


#TODO: this should be splitted in two parts, one that really is a model and
# other that emits the signals

class Resource(GObject.GObject):
    __gsignals__ = {
            'checked': (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    (STATUS_STARTED,
     STATUS_STOPPED,
     STATUS_ERROR) = range(3)

    def __init__(self, filename, interval):
        GObject.GObject.__init__(self)
        # just a placeholder
        self.key = str(random.randint(1, 1000))
        self.filename = filename
        self.interval = interval
        self.hash_value = ''
        self.added = datetime.datetime.now()
        self.last_checked = ''
        self.status_code = ''
        self.status_description = ''
        self.running_status = Resource.STATUS_STOPPED
        self.source_id = None

    def __str__(self):
        return '<Resource %s: %s - %s: %s>' % (self.key, self.filename,
                                               self.status_code,
                                               self.status_description)

    #
    # Private API
    #

    def _generate_hash_value(self, fp):
        hasher = hashlib.md5()
        data = fp.read()
        #  if we will parse the content and then generate the hash value
        #       the the value to generate the hash
        hasher.update(data)
        return hasher.digest()

    def _open_resource(self):
        try:
            self.last_checked = datetime.datetime.now().strftime('%x %X')
            resource = urllib2.urlopen(self.filename)
        except (urllib2.URLError, urllib2.HTTPError), e:
            self.status_code = e.errno
            if not e.errno and hasattr(e, 'code'):
                self.status_code = e.code

            self.status_description = e.message
            if not e.message and hasattr(e, 'msg'):
                self.status_description = e.msg

            if not self.status_description:
                self.status_description = str(e)
                self.status_code = self.status_code or 'ERROR'
            return
        except Exception, e:
            self.status_code = 'ERROR'
            self.status_description = e.message or str(e)
            self.source_id = None
            self.running_status = Resource.STATUS_STOPPED
            return

        return resource

    #
    # Public API
    #

    def check_change(self):
        if self.running_status == Resource.STATUS_STOPPED:
            self.source_id = None
            self.emit('checked')
            return False

        fp = self._open_resource()
        if fp is None:
            # if we don't have hash value set, then we have a status error, so
            # we don't need to check the file content.
            self.emit('checked')
            return bool(self.hash_value)

        hash_value = self._generate_hash_value(fp)
        self.status_code = fp.getcode() or 'OK'
        fp.close()

        if not self.hash_value:
            self.hash_value = hash_value

        if self.hash_value == hash_value:
            self.status_description = 'OK'
        else:
            self.hash_value = hash_value
            self.status_description = 'CHANGED'
            self.running_status = Resource.STATUS_STOPPED
            self.source_id = None
            send_message(self.status_description, self.filename)
            self.emit('checked')
            return False

        self.emit('checked')
        return True

    def can_start(self):
        return self.running_status != Resource.STATUS_STARTED

    def start(self):
        if self.can_start():
            self.running_status = Resource.STATUS_STARTED
            self.source_id = GLib.timeout_add_seconds(self.interval,
                                                      self.check_change)

    def can_stop(self):
        return self.running_status != Resource.STATUS_STOPPED

    def stop(self):
        if self.source_id and self.can_stop():
            self.running_status = Resource.STATUS_STOPPED
            if GLib.source_remove(self.source_id):
                self.source_id = None

    def has_changed(self):
        return self.status_description == 'CHANGED'


class ResourceManager(GObject.GObject):
    resources =  []
    __gsignals__ = {
            'added': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
            'edited': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
            'removed': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
            'started': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
            'stopped': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
            'resource-checked': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }

    def __init__(self):
        GObject.GObject.__init__(self)

    #
    # Public API
    #

    def get_resource_by_key(self, key):
        # placeholder, until we set a database backend
        for resource in self.resources:
            if resource.key == key:
                return resource

    def add_resource(self, resource):
        if resource not in self.resources:
            resource.connect('checked', self._on_resource__checked)
            self.resources.append(resource)
            resource.start()
            self.emit('added', resource)

    def remove_resource(self, resource):
        if resource in self.resources:
            self.resources.remove(resource)
            resource.stop()
            self.emit('removed', resource)

    def edited_resource(self, resource):
        if resource in self.resources:
            i = self.resources.index(resource)
            self.resources.remove(resource)
            resource.stop()
            resource.start()
            self.resources.insert(i, resource)
            self.emit('edited', resource)

    def start_resource(self, resource):
        if resource in self.resources:
            resource.start()
            self.emit('started', resource)

    def stop_resource(self, resource):
        if resource in self.resources:
            resource.stop()
            self.emit('stopped', resource)

    def has_resource_change(self):
        return any([r.has_changed() for r in self.resources])

    #
    # Callbacks
    #

    def _on_resource__checked(self, resource):
        self.emit('resource-checked', resource)
