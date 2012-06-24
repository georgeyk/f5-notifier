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

from utils import find_resource


class ResourceDialog(object):
    def __init__(self, parent):
        builder = Gtk.Builder()
        builder.add_from_file(find_resource('ui', 'AddResource.glade'))
        #builder.connect_signals(self)
        self.window = builder.get_object('AddResource')

    def run(self):
        return self.window.run()

    def destroy(self):
        return self.window.destroy()

    #
    # Callbacks
    #
