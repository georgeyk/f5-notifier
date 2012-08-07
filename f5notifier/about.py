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

import locale
from locale import gettext as _
locale.textdomain('f5-notifier')

from gi.repository import Gtk

import f5notifier
from f5notifier.utils import find_resource


def get_about_dialog(manager, parent):
    logo = Gtk.Image()
    icon_path = find_resource('images', 'f5notifier.svg')
    if icon_path:
        logo.set_from_file(icon_path)
    else:
        logo = None

    dialog = Gtk.AboutDialog(program_name=f5notifier.PROGRAM_NAME,
                             version=f5notifier.VERSION,
                             copyright=f5notifier.COPYRIGHT,
                             website=f5notifier.WEBSITE,
                             website_label=_(u'F5 Notifier Homepage'),
                             license_type=Gtk.License.GPL_3_0,
                             authors=f5notifier.AUTHORS,
                             flags=Gtk.DialogFlags.DESTROY_WITH_PARENT,
                             parent=parent)
    dialog.set_transient_for(parent)
    if icon_path:
        dialog.set_icon_from_file(icon_path)
    if logo:
        dialog.set_logo(logo.get_pixbuf())

    return dialog
