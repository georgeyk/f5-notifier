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

from gi.repository import GObject


class Resource(object):
    def __init__(self, filename, interval, check_now=True):
        self.filename = filename
        interval = interval
        self.hash_value = ''
        self.added = datetime.datetime.now()
        self.last_checked = ''
        self.status_code = ''
        self.status_description = ''
        if check_now:
            self.check_change()

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

    #
    # Public API
    #

    def check_change(self):
        try:
            f = urllib2.urlopen(self.filename)
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
            return True
        except ValueError, e:
            self.status_code = 'ERROR'
            self.status_description = e.message
            return False

        hash_value = self._generate_hash_value(f)
        f.close()
        self.status_code = f.getcode() or 'OK'

        if not self.hash_value:
            self.hash_value = hash_value

        if self.hash_value == hash_value:
            self.status_description = 'OK'
        else:
            self.hash_value = hash_value
            self.status_code = f.getcode() or 'OK'
            self.status_description = 'CHANGED'
            return False

        return True

    def start(self):
        pass

    def stop(self):
        pass


class ResourceManager(GObject.GObject):
    resources =  []
    __gsignals__ = {
            'added': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
            'edited': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
            'removed': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
            'started': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
            'stopped': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }

    def __init__(self):
        GObject.GObject.__init__(self)

    #
    # Public API
    #

    def add_resource(self, resource):
        # TODO: connect signals/callbacks
        self.resources.append(resource)
        self.emit('added', resource)

    def remove_resource(self, resource):
        self.resources.remove(resource)
        self.emit('removed', resource)

    def edited_resource(self, resource):
        self.emit('edited', resource)

    def start_resource(self, resource):
        if resource in self.resources:
            resource.start()
            self.emit('started', resource)

    def stop_resource(self, resource):
        if resource in self.resources:
            resource.stop()
            self.emit('stopped', resource)
