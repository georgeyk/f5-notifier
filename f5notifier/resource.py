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

from gi.repository import Gtk

from f5notifier.models import Resource
from f5notifier.utils import find_resource


class ResourceDialog(object):
    def __init__(self, manager, parent, resource=None):
        self._resource = resource
        builder = Gtk.Builder()
        builder.add_from_file(find_resource('ui', 'Resource.glade'))
        builder.connect_signals(self)
        self.window = builder.get_object('Resource')
        icon_file = find_resource('images', 'f5-notifier.svg')
        if icon_file:
            self.window.set_icon_from_file(icon_file)
        self.uri_entry = builder.get_object('uri_entry')
        self.unit_combo = builder.get_object('unit_combo')
        self.interval = builder.get_object('interval')
        self.interval_adjustment = builder.get_object('interval_adjustment')
        self.interval.set_value(5)
        self._manager = manager
        self._update_widgets()

    #
    # Private API
    #

    def _update_widgets(self):
        if self._resource:
            self.uri_entry.set_text(self._resource.data.filename)
            interval = self._resource.data.interval
            hour = 60 * 60
            if interval > hour:
                interval = interval / hour
                self.unit_combo.set_active(2)
            elif interval > 60:
                interval = interval / 60
                self.unit_combo.set_active(1)
            else:
                self.unit_combo.set_active(0)

            self.interval.set_value(interval)

    def _read_combo_unit_value(self):
        tree_iter = self.unit_combo.get_active_iter()
        if tree_iter != None:
            model = self.unit_combo.get_model()
            unit = model[tree_iter][0]
            return unit

    def _update_adjustment(self, unit):
        value = self.interval.get_value()
        if unit == 'seconds':
            self.interval_adjustment.set_lower(5)
            self.interval_adjustment.set_upper(59)
            if value < 5:
                self.interval.set_value(5)
        elif unit == 'hours':
            self.interval_adjustment.set_lower(1)
            self.interval_adjustment.set_upper(23)
            if value > 23:
                self.interval.set_value(23)
        else:
            self.interval_adjustment.set_lower(1)
            self.interval_adjustment.set_upper(59)

    def _get_interval_value(self):
        value = self.interval.get_value()
        unit = self._read_combo_unit_value()
        if unit == 'minutes':
            value = value * 60
        elif unit == 'hours':
            value = value * 60 * 60
        return int(value)

    def _save_resource(self):
        uri = self.uri_entry.get_text()
        interval = self._get_interval_value()
        if self._resource is None:
            resource = Resource(uri, interval)
            self._manager.add_resource(resource)
        else:
            self._resource.data.filename = uri
            self._resource.data.interval = interval
            self._manager.edited_resource(self._resource)

        # validate & message user

    #
    # Public API
    #

    def run(self):
        return self.window.run()

    def destroy(self):
        return self.window.destroy()

    #
    # Callbacks
    #

    def _on_add_button__clicked(self, widget):
        self._save_resource()

    def _on_filechooser_button__file_set(self, widget):
        uri = widget.get_uri()
        self.uri_entry.set_text(uri)

    def _on_unit_combo__changed(self, widget):
        self._update_adjustment(self._read_combo_unit_value())

    def _on_uri_entry__activate(self, widget):
        if widget.get_text():
            self._save_resource()
            self.destroy()
