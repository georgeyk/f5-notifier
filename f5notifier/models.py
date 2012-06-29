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

from gi.repository import GObject, GLib


#TODO: this should be splitted in two parts, one that really is a model and
# other that emits the signals

class Resource(GObject.GObject):
    __gsignals__ = {
            'checked': (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    (STATUS_STARTED,
     STATUS_STOPPED) = range(2)

    def __init__(self, filename, interval):
        GObject.GObject.__init__(self)

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
        return '<Resource: %s - %s: %s>' % (self.filename, self.status_code,
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
            resource = urllib2.urlopen(self.filename)
            self.last_checked = datetime.datetime.now()
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
            self.source_id = None
            self.emit('checked')
            return False

        self.emit('checked')
        return True

    def start(self):
        if self.source_id is None:
            self.running_status = Resource.STATUS_STARTED
            self.source_id = GLib.timeout_add_seconds(self.interval,
                                                      self.check_change)

    def stop(self):
        self.running_status = Resource.STATUS_STOPPED


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

    def add_resource(self, resource):
        # TODO: connect signals/callbacks
        if resource not in self.resources:
            resource.connect('checked', self._on_resource__checked)
            self.resources.append(resource)
            resource.start()
            self.emit('added', resource)
        else:
            print 'resource already added'

    def remove_resource(self, resource):
        if resource in self.resources:
            self.resources.remove(resource)
            resource.stop()
            self.emit('removed', resource)

    def edited_resource(self, resource):
        if resource in self.resources:
            self.emit('edited', resource)

    def start_resource(self, resource):
        if resource in self.resources:
            resource.start()
            self.emit('started', resource)

    def stop_resource(self, resource):
        if resource in self.resources:
            resource.stop()
            self.emit('stopped', resource)

    #
    # Callbacks
    #

    def _on_resource__checked(self, resource):
        print resource
        self.emit('resource-checked', resource)
