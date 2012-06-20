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

import pynotify


class Notificator(object):
    def __init__(self):
        pynotify.init('F5 Notifier')

    def send_message(self, title, message):
        note = pynotify.Notification(title, message)
        note.set_urgency(pynotify.URGENCY_NORMAL)
        note.show()

    def send_message_with_callback(self, title, message, button_label,
                                   callback):
        note = pynotify.Notification(title, message)
        note.set_urgency(pynotify.URGENCY_NORMAL)
        note.add_action('clicked', button_label, callback, None)
        note.show()


def _on_click_button(*args, **kwargs):
    print args, kwargs
    print 'clicked'


if __name__ == '__main__':
    notifier = Notificator()
    notifier.send_message('test', '123 foobar')
    notifier.send_message_with_callback('test', 'with callback', 'Click me',
                                        _on_click_button)
