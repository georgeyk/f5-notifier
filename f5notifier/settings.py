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

from f5notifier.utils import find_resource


class SettingsDialog(object):
    def __init__(self, manager, parent, settings):
        self._settings = settings
        builder = Gtk.Builder()
        builder.add_from_file(find_resource('ui', 'Settings.glade'))
        builder.connect_signals(self)
        self.window = builder.get_object('Settings')
        self.notification = builder.get_object('notification_switch')
        self.extra_filechooser = builder.get_object(
                                            'extra_settings_filechooser')
        self.extra_settings = builder.get_object('extra_settings_switch')

        self.notification.set_active(
                self._settings.get_value('DISABLE_NOTIFICATION'))
        self.extra_settings.set_active(
                self._settings.get_value('EXTRA_SETTINGS'))
        self.extra_filechooser.set_sensitive(self.extra_settings.get_active())
        self.extra_filechooser.select_filename(
                self._settings.get_value('EXTRA_SETTINGS_DIR'))

    def run(self):
        return self.window.run()

    def destroy(self):
        return self.window.destroy()

    #
    # Callbacks
    #

    def _on_extra_settings_switch__notify(self, widget, *args, **kwargs):
        is_active = widget.get_active()
        self.extra_filechooser.set_sensitive(is_active)

    def _on_apply_button__clicked(self, widget):
        self._settings.update_value('DISABLE_NOTIFICATION',
                                    self.notification.get_active())
        self._settings.update_value('EXTRA_SETTINGS',
                                    self.extra_settings.get_active())
        settings_dir = self.extra_filechooser.get_filename()
        self._settings.update_value('EXTRA_SETTINGS_DIR', settings_dir)
        self._settings.save()
