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


def get_about_dialog(manager, parent):
    logo = Gtk.Image()
    logo_path = find_resource('images', 'logo-64.png')
    if logo_path:
        logo.set_from_file(logo_path)
    else:
        logo = None

    dialog = Gtk.AboutDialog(program_name='F5 Notifier',
                             version='0.1',
                             copyright='2012 © George Kussumoto',
                             website='https://launchpad.net/f5-notifier',
                             website_label='F5 Notifier Homepage',
                             icon_name='gtk-about',
                             license_type=Gtk.License.GPL_3_0,
                             authors=['George Kussumoto'],
                             flags=Gtk.DialogFlags.DESTROY_WITH_PARENT,
                             parent=parent)
    dialog.set_transient_for(parent)
    if logo:
        dialog.set_logo(logo.get_pixbuf())

    return dialog
