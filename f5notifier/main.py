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

#from gettext import gettext as _
#import gettext
#gettext.textdomain('f5-notifier')

from gi.repository import AppIndicator3 as appindicator
from gi.repository import Gtk

from models import ResourceManager
from about import get_about_dialog
from resource import ResourceDialog
from resource_monitor import ResourceMonitor
from settings import SettingsDialog
from utils import find_resource, find_resources_dir, run_app_dialog


class F5Notifier(object):

    def __init__(self):
        self.indicator = appindicator.Indicator.new(
                'f5-notifier', 'indicator-messages-new',
                appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        images_dir = find_resources_dir('images')
        if images_dir:
            self.indicator.set_icon_theme_path(images_dir)
            self.indicator.set_icon('f5notifier')
            self.indicator.set_attention_icon('f5notifier-attention')

        menu = self._build_menu()
        self.indicator.set_menu(menu)
        self._manager = ResourceManager()

    #
    # Private API
    #

    def _build_menu(self):
        menu = Gtk.Menu()
        add_resource = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_ADD, None)
        add_resource.set_always_show_image(True)
        menu.append(add_resource)
        add_resource.connect('activate', self._on_add_resource__activated)
        add_resource.show()

        monitor_image = Gtk.Image.new_from_file(
                find_resource('images', 'f5notifier.svg'))
        monitor = Gtk.ImageMenuItem.new_with_label('Monitor')
        monitor.set_image(monitor_image)
        monitor.set_always_show_image(True)
        menu.append(monitor)
        monitor.connect('activate', self._on_monitor__activated)
        monitor.show()

        sep1 = Gtk.SeparatorMenuItem()
        menu.append(sep1)
        sep1.show()

        settings = Gtk.ImageMenuItem.new_from_stock(
                                            Gtk.STOCK_PREFERENCES, None)
        settings.set_always_show_image(True)
        menu.append(settings)
        settings.connect('activate', self._on_settings__activated)
        settings.show()

        sep2 = Gtk.SeparatorMenuItem()
        menu.append(sep2)
        sep2.show()

        about = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_ABOUT, None)
        about.set_always_show_image(True)
        menu.append(about)
        about.connect('activate', self._on_about__activated)
        about.show()

        quit = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_QUIT, None)
        quit.set_always_show_image(True)
        quit.connect('activate', self._on_quit__activated)
        quit.show()

        menu.append(quit)
        return menu

    #
    # Public API
    #

    def main(self):
        Gtk.main()

    #
    # Callbacks
    #

    def _on_add_resource__activated(self, widget):
        parent = widget.get_parent().get_parent()
        run_app_dialog(ResourceDialog, parent, self._manager)

    def _on_monitor__activated(self, widget):
        parent = widget.get_parent().get_parent()
        run_app_dialog(ResourceMonitor, parent, self._manager)

    def _on_settings__activated(self, widget):
        parent = widget.get_parent().get_parent()
        run_app_dialog(SettingsDialog, parent, self._manager)

    def _on_about__activated(self, widget):
        parent = widget.get_parent().get_parent()
        run_app_dialog(get_about_dialog, parent)

    def _on_quit__activated(self, widget):
        Gtk.main_quit()


# testing

if __name__ == '__main__':
    f5 = F5Notifier()
    f5.main()
