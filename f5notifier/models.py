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
import os
import os.path

try:
    import cPickle as pickle
except Exception:
    import pickle

import random
import urllib2

from gi.repository import GObject, GLib

from f5notifier.notification import send_message


#TODO: this should be splitted in two parts, one that really is a model and
# other that emits the signals

class ResourceData(object):
    def __init__(self, filename, interval, key='', hash_value='',
                 added='', last_checked='', status_code='',
                 status_description='', running_status=''):

        self.filename = filename
        self.interval = interval
        self.key = key
        if not key:
            self.key = str(random.randint(1, 10000))
        self.hash_value = hash_value
        self.added = added
        if not added:
            self.added = datetime.datetime.now()
        self.last_checked = last_checked
        self.status_code = status_code
        self.status_description = status_description
        self.running_status = running_status
        self.source_id = None


class Resource(GObject.GObject):
    __gsignals__ = {
            'checked': (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    (STATUS_STARTED,
     STATUS_STOPPED,
     STATUS_ERROR) = range(3)

    def __init__(self, filename, interval):
        GObject.GObject.__init__(self)
        # just a placeholder, fix pickle with GObject.
        self.data = ResourceData(filename, interval)

    def __str__(self):
        return '<Resource %s: %s - %s: %s>' % (self.data.key,
            self.data.filename, self.data.status_code,
            self.data.status_description)

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
            self.data.last_checked = datetime.datetime.now().strftime('%x %X')
            resource = urllib2.urlopen(self.data.filename)
        except (urllib2.URLError, urllib2.HTTPError), e:
            self.data.status_code = 'ERROR'

            self.status_description = e.message
            if not e.message and hasattr(e, 'msg'):
                self.data.status_description = e.msg

            if not self.status_description:
                self.data.status_description = str(e)
            return
        except Exception, e:
            self.data.status_code = 'ERROR'
            self.data.status_description = e.message or str(e)
            self.data.source_id = None
            self.data.running_status = Resource.STATUS_STOPPED
            return

        return resource

    #
    # Public API
    #

    def check_change(self):
        if self.data.running_status == Resource.STATUS_STOPPED:
            self.data.source_id = None
            self.emit('checked')
            return False

        fp = self._open_resource()
        if fp is None:
            # if we don't have hash value set, then we have a status error, so
            # we don't need to check the file content.
            self.emit('checked')
            return bool(self.data.hash_value)

        hash_value = self._generate_hash_value(fp)
        self.data.status_code = 'RUNNING'
        fp.close()

        if not self.data.hash_value:
            self.data.hash_value = hash_value

        if self.data.hash_value == hash_value:
            self.data.status_description = 'OK'
        else:
            self.data.hash_value = hash_value
            self.data.status_code = 'STOPPED'
            self.data.status_description = 'CHANGED'
            self.data.running_status = Resource.STATUS_STOPPED
            self.data.source_id = None
            send_message(self.data.status_description, self.data.filename)
            self.emit('checked')
            return False

        self.emit('checked')
        return True

    def can_start(self):
        return self.data.running_status != Resource.STATUS_STARTED

    def start(self):
        if self.can_start():
            self.data.running_status = Resource.STATUS_STARTED
            self.data.status_code = 'RUNNING'
            self.data.source_id = GLib.timeout_add_seconds(self.data.interval,
                                                           self.check_change)

    def can_stop(self):
        return self.data.running_status != Resource.STATUS_STOPPED

    def stop(self):
        if self.data.source_id and self.can_stop():
            self.data.running_status = Resource.STATUS_STOPPED
            self.data.status_code = 'STOPPED'
            if GLib.source_remove(self.data.source_id):
                self.data.source_id = None

    def has_changed(self):
        return self.data.status_description == 'CHANGED'


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

    def __init__(self, settings):
        self._settings = settings
        GObject.GObject.__init__(self)
        for data in self._settings.get_data_resources():
            resource = Resource(data.filename, data.interval)
            resource.data = data
            #self.resources.append(resource)
            self.add_resource(resource)

    #
    # Public API
    #

    def get_resource_by_key(self, key):
        # placeholder, until we set a database backend
        for resource in self.resources:
            if resource.data.key == key:
                return resource

    def add_resource(self, resource):
        if resource not in self.resources:
            resource.connect('checked', self._on_resource__checked)
            self.resources.append(resource)
            resource.start()
            self._settings.add_resource(resource)
            self.emit('added', resource)

    def remove_resource(self, resource):
        if resource in self.resources:
            self.resources.remove(resource)
            resource.stop()
            self._settings.remove_resource(resource)
            self.emit('removed', resource)

    def edited_resource(self, resource):
        if resource in self.resources:
            i = self.resources.index(resource)
            self.resources.remove(resource)
            resource.stop()
            resource.start()
            self.resources.insert(i, resource)
            self._settings.update_resource(resource)
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


class SettingsManager(object):
    DEFAULT_DIR = '~/.config/f5-notifier/'
    CONF_FP = 'config'
    CONF_DATA = {'DISABLE_NOTIFICATION': True,
                 'IGNORE_STATUS_CHANGE': True,
                 'EXTRA_SETTINGS': False,
                 'EXTRA_SETTINGS_DIR': '',
                 'FILES': [],}

    def __init__(self):
        self._default_path = os.path.expanduser(self.DEFAULT_DIR)
        if not os.path.isdir(self._default_path):
            os.mkdir(self._default_path)

        if not os.path.isfile(os.path.join(self._default_path, self.CONF_FP)):
            # Create a default settings file.
            self.save()

        self._load_settings()

    #
    # Private API
    #

    def _create_default_settings(self):
        pass

    def _get_data_from_file(self, filename):
        try:
            fp = open(filename)
            data = pickle.load(fp)
            fp.close()
        except Exception:
            return {}

        return data

    def _get_file(self, extra=False):
        datafile = os.path.join(self._default_path, self.CONF_FP)

        return datafile

    def _load_settings(self):
        conf_data = self._get_data_from_file(self._get_file())
        if conf_data and type(conf_data) == dict:
            self.CONF_DATA.update(conf_data)

    #
    # Public API
    #

    def add_resource(self, resource):
        if resource.data not in self.CONF_DATA['FILES']:
            self.CONF_DATA['FILES'].append(resource.data)

    def remove_resource(self, resource):
        if resource.data in self.CONF_DATA['FILES']:
            self.CONF_DATA['FILES'].remove(resource.data)

    def update_resource(self, resource):
        if resource.data in self.CONF_DATA['FILES']:
            i = self.CONF_DATA['FILES'].index(resource.data)
            self.remove_resource(resource)
            self.CONF_DATA['FILES'].insert(i, resource.data)

    def get_data_resources(self):
        return self.CONF_DATA['FILES']

    def update_value(self, key, value):
        if key in self.CONF_DATA.keys():
            self.CONF_DATA[key] = value

    def save(self):
        conf = open(self._get_file(), 'w+')
        pickle.dump(self.CONF_DATA, conf)
        conf.close()
