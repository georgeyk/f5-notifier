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

from utils import yesno, find_resource, open_file


class ResourceMonitor(object):
    def __init__(self, manager, parent):
        self._parent = parent
        builder = Gtk.Builder()
        builder.add_from_file(find_resource('ui', 'ResourceMonitor.glade'))
        builder.connect_signals(self)
        self.window = builder.get_object('ResourceMonitor')
        self.add_button = builder.get_object('add_button')
        self.edit_button = builder.get_object('edit_button')
        self.remove_button = builder.get_object('remove_button')
        self.open_button = builder.get_object('open_button')
        self.start_button = builder.get_object('start_button')
        self.stop_button = builder.get_object('stop_button')
        self.resource_selection = builder.get_object('resource_selection')
        self._update_widgets()

    #
    # Private API
    #

    def _update_widgets(self, selected=None):
        needs_selection_buttons =  [self.edit_button, self.remove_button,
                                    self.open_button, self.start_button,
                                    self.stop_button]
        for button in needs_selection_buttons:
            button.set_sensitive(bool(selected))

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

    def _on_open_button__clicked(self, widget):
        selection, tree_iter = self.resource_selection.get_selected()
        if tree_iter:
            selected = selection[tree_iter][0]
            #XXX: it seems that setting the parent fixes the 'operation not
            # permitted' exception. I really don't know why, since it its not
            # used by open_file in case of success. :S annoying
            open_file(selected, parent=self._parent)

    def _on_remove_button__clicked(self, widget):
        retval = yesno('Remove Resource',
                    'Are you sure you want to remove the selected resource ?',
                     parent=self._parent)
        if retval == Gtk.ResponseType.YES:
            pass
            # get resource and remove it

    def _on_resource_view__selection_changed(self, selection):
        model, tree_iter = selection.get_selected()
        if tree_iter:
            selected = model[tree_iter][0]
        else:
            selected = None

        self._update_widgets(selected)
