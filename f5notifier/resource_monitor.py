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

from resource import ResourceDialog
from utils import yesno, find_resource, open_file, run_app_dialog


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
        self.resources_list = builder.get_object('resources_list')

        manager.connect('added', self._on_resource__added)
        manager.connect('edited', self._on_resource__edited)
        manager.connect('removed', self._on_resource__removed)
        manager.connect('started', self._on_resource__started)
        manager.connect('stopped', self._on_resource__stopped)
        manager.connect('resource-checked', self._on_resource__checked)
        self._manager = manager

        self._update_widgets()
        self._load_data()

    #
    # Private API
    #

    def _update_widgets(self, selected=None):
        needs_selection_buttons =  [self.edit_button, self.remove_button,
                                    self.open_button, self.start_button,
                                    self.stop_button]
        for button in needs_selection_buttons:
            button.set_sensitive(bool(selected))

    def _load_data(self):
        for resource in self._manager.resources:
            self._add_resoure(resource)

    def _find_iter_for_resource(self, resource):
        list_iter = self.resources_list.get_iter_first()
        while True:
            if not list_iter:
                break

            resource_id = self.resources_list.get_value(list_iter, 0)
            if resource_id == resource.key:
                return list_iter

            list_iter = self.resources_list.iter_next(list_iter)

    def _add_resoure(self, resource):
        list_iter = self._find_iter_for_resource(resource)
        if list_iter is None:
            self.resources_list.append([resource.key,
                                        resource.filename,
                                        str(resource.status_code),
                                        resource.status_description,
                                        resource.last_checked])

    def _remove_resource(self, resource):
        list_iter = self._find_iter_for_resource(resource)
        if list_iter:
            self.resources_list.remove(list_iter)

    def _update_resource(self, resource):
        list_iter = self._find_iter_for_resource(resource)
        if list_iter:
            self.resources_list.set_value(list_iter, 1, resource.filename)
            self.resources_list.set_value(list_iter, 2,
                                          str(resource.status_code))
            self.resources_list.set_value(list_iter, 3,
                                          resource.status_description)
            self.resources_list.set_value(list_iter, 4,
                                          resource.last_checked)

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
        parent = widget.get_parent().get_parent()
        run_app_dialog(ResourceDialog, parent, self._manager)

    def _on_edit_button__clicked(self, widget):
        parent = widget.get_parent().get_parent()
        model, tree_iter = self.resource_selection.get_selected()
        if tree_iter:
            key = model[tree_iter][0]
            resource = self._manager.get_resource_by_key(key)
        else:
            resource = None

        run_app_dialog(ResourceDialog, parent, self._manager,
                       resource=resource)

    def _on_remove_button__clicked(self, widget):
        retval = yesno('Remove Resource',
                    'Are you sure you want to remove the selected resource ?',
                     parent=self._parent)
        if retval == Gtk.ResponseType.YES:
            model, tree_iter = self.resource_selection.get_selected()
            if tree_iter:
                key = model[tree_iter][0]
                resource = self._manager.get_resource_by_key(key)
                self._manager.remove_resource(resource)

    def _on_open_button__clicked(self, widget):
        selection, tree_iter = self.resource_selection.get_selected()
        if tree_iter:
            selected = selection[tree_iter][1]
            #XXX: it seems that setting the parent fixes the 'operation not
            # permitted' exception. I really don't know why, since it its not
            # used by open_file in case of success. :S annoying
            open_file(selected, parent=self._parent)

    def _on_start_button__clicked(self, widget):
        model, tree_iter = self.resource_selection.get_selected()
        if tree_iter:
            key = model[tree_iter][0]
            resource = self._manager.get_resource_by_key(key)
            self._manager.start_resource(resource)

    def _on_stop_button__clicked(self, widget):
        model, tree_iter = self.resource_selection.get_selected()
        if tree_iter:
            key = model[tree_iter][0]
            resource = self._manager.get_resource_by_key(key)
            self._manager.stop_resource(resource)

    def _on_resource_view__selection_changed(self, selection):
        model, tree_iter = selection.get_selected()
        if tree_iter:
            selected = model[tree_iter][1]
        else:
            selected = None
        self._update_widgets(selected)

    def _on_resource__added(self, manager, resource):
        self._add_resoure(resource)

    def _on_resource__edited(self, manager, resource):
        self._update_resource(resource)

    def _on_resource__removed(self, manager, resource):
        self._remove_resource(resource)

    def _on_resource__started(self, manager, resource):
        self._update_resource(resource)

    def _on_resource__stopped(self, manager, resource):
        self._update_resource(resource)

    def _on_resource__checked(self, manager, resource):
        self._update_resource(resource)
