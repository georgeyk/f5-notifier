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

import os.path
import time

from gi.repository import Gtk
from gi._glib import GError


def warn_user(title, message, parent=None):
    dialog = Gtk.MessageDialog(parent, 0, Gtk.MessageType.WARNING,
                               Gtk.ButtonsType.OK, title)
    dialog.format_secondary_text(message)
    dialog.run()
    dialog.destroy()

def yesno(title, message, parent):
    flags = Gtk.DialogFlags.MODAL
    dialog = Gtk.MessageDialog(parent, flags, Gtk.MessageType.QUESTION,
                               Gtk.ButtonsType.YES_NO, title)
    dialog.format_secondary_text(message)
    retval = dialog.run()
    dialog.destroy()
    return retval

def open_file(uri, show_dialog=True, parent=None):
    # Currently, we just support local and web files, defaults to local files.
    if not uri.startswith('http://') or not uri.startswith('file:///'):
        uri = 'file://' + uri

    try:
        retval = Gtk.show_uri(None, uri, time.time())
    except GError, e:
        retval = False
        if show_dialog:
            warn_user('Error', e.message, parent=parent)

    return retval

def find_resources_dir(resource_type):
    data_dir = os.path.realpath('../data')
    directory = data_dir + '/' + resource_type
    if os.path.isdir(directory):
        return directory

def find_resource(resource_type, resource_name):
    resource_dir = find_resources_dir(resource_type)
    if resource_dir:
        filepath = resource_dir + '/' + resource_name
        if os.path.isfile(filepath):
            return filepath
