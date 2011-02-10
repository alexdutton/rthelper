#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64, os, tempfile, re
import urllib, urllib2, urlparse, cookielib
import webbrowser
from StringIO import StringIO
from xml.sax import saxutils
from functools import partial, wraps

from lxml import etree
import gtk
import pynotify
import gnomekeyring

APPLICATION_NAME = 'rt-helper'

# Change these to use other RT instances.
RT_URL = 'https://rt.oucs.ox.ac.uk/'
# Currently supported authentication: 'oxford-webauth', 'standard'
AUTHENTICATION = 'oxford-webauth'

# These are base64-encoded PNGs which will be written to temporary files
# and then read back into pixbufs for Gnome's delectation.
ICONS = {
    'ok': """\
iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlz
AAAN1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJwSURB
VFiF5Zc9aBRBFMd/c2qihxYmIBE5tNDCKgpRUQiIgqBgZy0YDgvFQgwIWh/40QWMwVZQlKCHSEBE
sPQjhR+IGCziKX6jYlBzJHd/i73lJnNzu7cX1hQ+GNjdee/9f/NmZnfWSGIhLbOg6v8EwJgVGDOG
MSWMOd7QLyndBhcEslqX3W9SXQPGbAbGqVf6D7AcqRq6pDcFxhhg2NE4a4sDKU4BDDilfy1Y6vql
Jb5S8MUB2OfzTQtg2BEvNvNtughNMIc7gbVJpv4Y9AxBgbkLbyPSG2+AtywwAEwAStIM6MHckUtw
OqpaPvFVQDmpOKC8I/4dPgo6owAWe4pyCOioXT8DrgOzcaVfD9khGASy4bM8TI1K5chATwVuWqPa
kmDhjdijH63niKxAGLxD8FYwUQhGHQava1G8T1AJxX9DJVfP0bD3fQA3bPoiqKtVAMgIHtnxBXhP
QgB336oEug0HWgA47MS+7ISnSQGygqsuRBVmBacEmSbi3YKvTtxu4EkygHrC/HQgKqfdFfR4AC45
ftdqC7lNAIntcO95I4AEnwR7LPGtgqrVPyVYM28AoLgMNOKHqArOCDoEj52+QSvH/ADC4HE4Ivjh
ASk59y8ES9oBiDyQ9MEYsAl46HTlnPujSDNRuZpZ/IlImgT6gXMEI3LtCtL9dsRbAwggZpBOAnuB
z1bPT4L3f9vmA/hlXe9yQO4AvcB54BbQj/TBdjHG5IANtdsyMR+yhgOJMWZ/LXlo74BKVBLHVlP/
ml6WdDDS27MLFgGTtHEe8LRtca9y/0PoBk4Ar4DphO0bcBHojf2OKO0fkxbsP/g5jbG/pq4LvQ3X
aHgAAAAASUVORK5CYII=""",
    'error': """\
iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlz
AAAN1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAASVSURB
VFiFxZdZbFRlFMd/3+1G22npFL2l9DYsMi1bZOlAw1rHGG0m2Kc+iNUaazFG2wcRAwIxJixqTHxA
IQhiaklQKCp04gRjMSEQMYqdMpWkgg+Urk6XWBHaYtvjw7RlOnOni3HkS04y91vO/3/+59z7nVEi
wv0c2n1F/18IKJWEUm6UuolSr4asi0hkDQ4ISIClBq6riNaAUsuBy9xTuhewIDI0siVyKVBKAQeD
MN4NBAcimAIoCZL+N4FpwfsiBW4V6Agi4DTbGykCB4PAT4fbG7YIlT+HjwCzp5L6Mpj5AexlbOEt
RKTR9ICpLFACXANkKqZAfhgbuQjsHE8tM3Ad6J8qOCClQeB/QLtA3HgEok1EeR6IHf7tBU4CAxNJ
Px8S9sNWIGFk7gW4dUqkf9yDJgp8FRDVyikU3qHA6E/d8zEJBZRaA5wAevdA3657/Dominz4vJ2Y
mM3k5UFuLjfmzZM7SqkDvb0UFxdvBr4Ffg2vAHwZyP40SKqf/ZxJRK5JXt7VS8ePi9PplAdnzBit
CU3TJNtmk7KyMmlpaflERJLMizD0vZWbIC4onIjAnZMnz7yxfbtEaZro8fHyjGHI+4sXywm7XXZm
ZckTui6aUmLMmiUul+t3EVlhRiBB4LNgEkMwILBDQDMlcO3a00VFRQLIpowM6crPFykoCLEL69bJ
QxaLKKWkurq6PVCJsR8ipUr74VAcRAVlqgZ4FpH2gLkHvjh2rKWwuDh2h83G3oULxy2TvwYGyLl4
kd6kJC7X1lbquv4cBN+GIh874PwvoecfA66g1OMjEz21tQde3rIldrnVylvZ2eOCA1iio6lcupTW
tjZ2795dDCwNJQBcglurgI9CfejAWZR6B6ViPV5vga+zkzdtNmK0yd3quVYrG3Wdr10ugPWA6YeI
XuAlwA6v5MA+YPrwkgK2ERdX5OnsnAZgnz68lJ0NiYnh0RsboasLe0oKZxoaaG5uXmMYxoemBEaG
HdwCbuBzIHd0Yf58w3v1Kta4OIz4eP9caSlkZYV3tn8/nDvHw8nJAHi93hWGYZgrMGaI3ECp9cAe
4HVA4fORlpbGn3fvcmdwkISoKGhogNu3w/vp6gKgra8PAF3X2yBMCkxI/A1sQ6nvgEo6OnT7nDkM
ilDX08Oa1FQ4enRSrn7u6SEpMZFly5ZdAPOeMDCMR4OIfIO/et/LSUnxKaWoam2dFDD4X8WznZ2s
XLWK6Ojon4DQhkQp9SRQHTDVDAwGO3M6ndMyMzPTjhw+zPm1a1mXmjohgRevXOFoUxM1NTVNDofD
BvSbKeAGArsXA39XNMbcbnfaggULMDIyKPJ4+L67OyzwoAhvX7/OkcZGysvLxeFwPIW/5wjbEc0A
XsN/g/WFM4vF0ldVVTU0OzNTNKWkfO5c+XHDBunbuFGkoEB8+fniys2VHKtVACksLJTu7u59/3VT
muTz+T4tKSkZvQVjNE3SExJGn1OSk6WiouKWiGyadFP6L4azrq5uq8fjWVFfXz+9tbWVJUuWDC1a
tKhp9erVNenp6buA9uBDkfprlgHMBBoY+1aFjH8AmUuNOPMw1RcAAAAASUVORK5CYII=""" }

class CredentialManager(object):
    " Handles storing and retrieving SSO credentials from the Gnome keyring "

    def __init__(self):
        self._item_id = None
        self._keyring = None

    @property
    def username(self):
        if not hasattr(self, '_username'):
            self._fetch_credentials()
        return self._username

    @property
    def password(self):
        if not hasattr(self, '_password'):
            self._fetch_credentials()
        return self._password

    def _fetch_credentials(self):
        " Retrieves credentials from the Gnome keyring "
        try:
            finds = gnomekeyring.find_items_sync(gnomekeyring.ITEM_GENERIC_SECRET,
                                                 {'application': APPLICATION_NAME})
        except gnomekeyring.NoMatchError:
            self._username, self._password = None, None
            return
        for find in finds:
            self._keyring, self._item_id = find.keyring, find.item_id
            item = gnomekeyring.item_get_info_sync(find.keyring, find.item_id)
            attributes = gnomekeyring.item_get_attributes_sync(find.keyring, find.item_id)
            self._username = attributes['username']
            self._password = item.get_secret()
            break
        else:
            self._username, self._password = None, None

    def acquire_credentials(self):
        """
        Asks the user for their SSO credentials. If they are provided they are 
        provided then they are stored in the Gnome keyring.
        """
        dialog = gtk.MessageDialog(None,
                                   gtk.DIALOG_MODAL,
                                   gtk.MESSAGE_QUESTION,
                                   gtk.BUTTONS_OK_CANCEL,
                                   None)
        try:
            dialog.set_markup("Please enter your SSO credentials:")
            table = gtk.Table(2, 2)

            username = gtk.Entry()
            table.attach(gtk.Label('Username:'), 0, 1, 0, 1, xpadding=5, ypadding=5)
            table.attach(username, 1, 2, 0, 1, xpadding=5, ypadding=5)

            password = gtk.Entry()
            password.set_visibility(False)
            table.attach(gtk.Label('Password:'), 0, 1, 1, 2, xpadding=5, ypadding=5)
            table.attach(password, 1, 2, 1, 2, xpadding=5, ypadding=5)

            username.connect('activate', lambda event:password.grab_focus())
            password.connect('activate', lambda event:dialog.response(gtk.RESPONSE_OK))

            dialog.vbox.pack_end(table, True, True, 0)
            dialog.show_all()
            if dialog.run() != gtk.RESPONSE_OK:
                raise ValueError('Password dialog cancelled')
            self._set_credentials(username.get_text(), password.get_text())
        finally:
            dialog.destroy()

    def _set_credentials(self, username, password):
        " Stores the username and password in the Gnome keyring. "
        self._fetch_credentials()
        self._username, self._password = username, password

        if self._item_id:
            gnomekeyring.item_delete_sync(self._keyring, self._item_id)

        self._keyring = 'login'
        self._item_id = gnomekeyring.item_create_sync(self._keyring,
                                                      gnomekeyring.ITEM_GENERIC_SECRET,
                                                      'rt-helper',
                                                      {'application': APPLICATION_NAME,
                                                       'username': username},
                                                      password, False)

class BadCredentialsError(Exception):
    pass
class RequestCancelledError(Exception):
    pass

class RTOpener(object):
    def __init__(self, credentials):
        self._credentials = credentials
        self._opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))

    def __getattr__(self, name):
        return getattr(self._opener, name)

class WebAuthRTOpener(RTOpener):
    """
    An urllib2 opener object that has the right cookies to access a
    WebAuth-protected service.
    """
    def __init__(self, credentials, webauth_url):
        super(WebAuthRTOpener, self).__init__(credentials)
        self._webauth_url = webauth_url

    def open(self, *args, **kwargs):
        response = self._opener.open(*args, **kwargs)

        if response.geturl().startswith(self._webauth_url):
            response = self._authenticate(response)

        return _RTOpenerResponse(response)

    def _authenticate(self, response):
        if not (self._credentials.username and self._credentials.password):
            raise BadCredentialsError

        login_page = etree.parse(response, parser=etree.HTMLParser())
        post_data = {}
        for node in login_page.xpath('.//input'):
            post_data[node.get('name')] = node.get('value')
        post_data['username'] = self._credentials.username
        post_data['password'] = self._credentials.password

        intermediate_url = urlparse.urljoin(response.geturl(), login_page.xpath('.//form')[0].attrib['action'])
        intermediate_page = etree.parse(self._opener.open(intermediate_url, urllib.urlencode(post_data)), parser=etree.HTMLParser())

        go_button = intermediate_page.xpath('.//td/p/span/a')
        if not go_button:
            raise BadCredentialsError

        return self._opener.open(go_button[0].attrib['href'])

class RTResult(object):
    (USER_ALREADY_OWNS_TICKET, TICKET_NOT_UNOWNED, OWNER_CHANGED,
     STATUS_CHANGED, CANT_REASSIGN, NO_SUCH_USER, NO_SUCH_QUEUE,
     QUEUE_CHANGED) = range(1, 9)

    _PATTERNS = {
        USER_ALREADY_OWNS_TICKET: r'^That user already owns that ticket$',
        TICKET_NOT_UNOWNED: r'^You can only take tickets that are unowned$',
        OWNER_CHANGED: r'^Owner changed from (?P<old_owner>.+) to (?P<new_owner>.+)$',
        STATUS_CHANGED: r"^Ticket \d+: Status changed from '(?P<old_status>\w+)' to '(?P<new_status>\w+)'$",
        CANT_REASSIGN: r'^You can only reassign tickets that you own or that are unowned$',
        NO_SUCH_USER: r'^That user does not exist$',
        NO_SUCH_QUEUE: r'^That queue does not exist$',
        QUEUE_CHANGED: r'^Ticket \d+: Queue changed from (?P<old_queue>\w+) to (?P<new_queue>\w+)$',
    }
    _PATTERNS = [(a,re.compile(b)) for a,b in _PATTERNS.items()]

    def __init__(self, elem):
        text = ' '.join(elem.text.split())
        for ptype, pattern in self._PATTERNS:
            match = pattern.match(text)
            if match:
                self._ptype = ptype
                for name, value in match.groupdict().items():
                     setattr(self, name, value)
                break
        else:
             raise AssertionError('Unexpected result: %r' % text)

    def __eq__(self, other):
        return self._ptype == other
    def __ne__(self, other):
        return self._ptype != other

class _RTOpenerResponse(object):
    def __init__(self, response):
        self._response = response
        self.xml = etree.parse(response, parser=etree.HTMLParser())
        self.results = map(RTResult, self.xml.xpath(".//ul[@class='action-results']/li"))
        self.result = self.results[0] if self.results else None
        self.owner = ' '.join(self.xml.xpath(".//div[contains(@class, 'ticket-info-people')]//td[2]")[0].text.split())
        
    def __getattr__(self, name):
        return getattr(self._response, name)

class StandardRTOpener(RTOpener):
    """ An urllib2 opener that can handle RT's built-in authentication. """
    def open(self, *args, **kwargs):
        second_attempt = kwargs.pop('second_attempt', False)
        response = _RTOpenerResponse(self._opener.open(*args, **kwargs))

        if response.xml.xpath(".//form[@id='login']"):
            if second_attempt:
                raise BadCredentialsError
            return self._authenticate(response, page)
        else:
            return response

    def _authenticate(self, response, page):
        form = page.xpath(".//form[@id='login']")[0]
        post_data = {}
        for node in form.xpath('.//input'):
            if 'name' in node.attrib:
                post_data[node.attrib['name']] = node.attrib.get('value', '')
        post_data['user'] = self._credentials.username
        post_data['pass'] = self._credentials.password

        url = urlparse.urljoin(response.geturl(), form.attrib['action'])
        return self.open(url, urllib.urlencode(post_data), second_attempt=True)

AUTHENTICATION_METHODS = {
    'oxford-webauth': lambda credentials: WebAuthRTOpener(credentials, 'https://webauth.ox.ac.uk/'),
    'standard': StandardRTOpener,
}

class RTHelper(object):
    def __init__(self):
        self._statusicon = gtk.StatusIcon()
        self._statusicon.connect('popup-menu', self._show_menu)

        self._load_icons()

        self._credentials = CredentialManager()
        self._opener = None
        self._ticket= None
        self._notifications = set()
        self._opener = AUTHENTICATION_METHODS[AUTHENTICATION](self._credentials)

        self._clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_PRIMARY)
        self._clipboard.connect('owner-change', self._clipboard_changed)
        self._clipboard_changed(self._clipboard, None)

    def _load_icons(self):
        " Decodes, saves and loads pixbufs for the applet icon. "
        self._icons = {}
        for name, data in ICONS.items():
             f = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
             f.write(base64.b64decode(data))
             f.close()
             self._icons[name] = gtk.gdk.pixbuf_new_from_file(f.name)
             os.unlink(f.name)

    def _clipboard_changed(self, clipboard, event):
        text = clipboard.wait_for_text()
        if text is None and self._ticket:
            return
        if not text:
            self._ticket= None
        else:
            if text.startswith('#'):
                text = text[1:]
            self._ticket= text if text.isdigit() else None

        if self._ticket is not None:
            self._statusicon.set_from_pixbuf(self._icons['ok'])
        else:
            self._statusicon.set_from_pixbuf(self._icons['error'])

    def _show_menu(self, icon, button, time):
        menu = gtk.Menu()
        command = Command(self._ticket, self._request, self._notify)

        if self._ticket is not None:
            show = gtk.MenuItem("Show")
            show.connect('activate', command.show)
            menu.append(show)

            menu.append(gtk.SeparatorMenuItem())

            item = gtk.MenuItem("Take")
            item.connect('activate', command.take)
            menu.append(item)

            item = gtk.MenuItem("Take and set open")
            item.connect('activate', command.take_and_set_open)
            menu.append(item)

            if 'actions' not in self._notify.caps:
                item = gtk.MenuItem("Steal")
                item.connect('activate', command.steal)
                menu.append(item)

            menu.append(gtk.SeparatorMenuItem())

            item = gtk.MenuItem(u"Give ticket to…")
            item.connect('activate', command.give)
            menu.append(item)

            item = gtk.MenuItem(u"Change queue…")
            item.connect('activate', command.change_queue)
            menu.append(item)

            menu.append(gtk.SeparatorMenuItem())

            for label, status in [('Set open', 'open'), ('Quick resolve', 'resolved'), ('Quick reject', 'rejected'), ('Delete', 'deleted')]:
                # This needs wrapping in a function to provide a separate closure for each reference to status
                def f(status):
                    return 
                item = gtk.MenuItem(label)
                item.connect('activate', command.change_status(new_status=status, partial=True))
                menu.append(item)

            menu.append(gtk.SeparatorMenuItem())

        quit = gtk.MenuItem("Quit")
        quit.connect('activate', gtk.main_quit)
        menu.append(quit)

        menu.show_all()
        menu.popup(None, None, gtk.status_icon_position_menu, button, time, self._statusicon)

    def _request(self, url):
        if isinstance(url, (list, dict, tuple)):
            url = RT_URL + 'Ticket/Display.html?%s' % urllib.urlencode(url)
        while True:
            try:
                return self._opener.open(url)
            except BadCredentialsError:
                try:
                    self._credentials.acquire_credentials()
                except ValueError:
                    raise RequestCancelledError

    def _notify(self, title, body, icon, actions, ticket, with_ticket_number=True):
        if with_ticket_number:
            title = '#%s - %s' % (ticket, title)

        notification = pynotify.Notification(title, body, icon)

        if 'actions' in self._notify.caps:
            for action in actions:
                notification.add_action(action.__name__, action.label, action)

        notification.set_timeout(5000)
        self._notifications.add(notification)
        notification.connect('closed', lambda n: self._notifications.remove(n))
        notification.show()
    _notify.caps = set(pynotify.get_server_caps())

def action(label):
    def g(func):
        def p(func, self, **kwargs):
            func = wraps(func)(partial(func, self, **kwargs))
            func.label = label
            return func
        @wraps(func)
        def f(self, *args, **kwargs):
            if kwargs.pop('partial', False):
                return p(f, self, **kwargs)
            try:
                return func(self, **kwargs)
            except RequestCancelledError:
                self._notify('Request cancelled', 'You have not changed the status of this ticket.',
                             gtk.STOCK_DIALOG_ERROR, [self.show])
            except Exception, e:
                print repr(e)
                raise
        f.label = label
        return f
    return g

class Command(object):
    def __init__(self, ticket, request_func, notify_func):
        self._ticket = ticket
        self._request = request_func
        self._notify = wraps(notify_func, ('caps',))(partial(notify_func, ticket=ticket))

    def _ask_question(self, title, question, prompt):
        dialog = gtk.MessageDialog(None,
                                   gtk.DIALOG_MODAL,
                                   gtk.MESSAGE_QUESTION,
                                   gtk.BUTTONS_OK_CANCEL,
                                   None)
        try:
            dialog.set_title(title)
            dialog.set_markup(question)
            hbox = gtk.HBox()

            entry = gtk.Entry()
            entry.connect('activate', lambda event:dialog.response(gtk.RESPONSE_OK))
            hbox.pack_start(gtk.Label(prompt), False, 5, 5)
            hbox.pack_end(entry)

            dialog.vbox.pack_end(hbox, True, True, 0)
            dialog.show_all()
            if dialog.run() != gtk.RESPONSE_OK:
                raise ValueError('Dialog cancelled')
            dialog.hide_all()
            return entry.get_text()
        finally:
            dialog.destroy()

    @action(label='Show')
    def show(self):
        webbrowser.open(RT_URL + 'Ticket/Display.html?id=' + self._ticket)

    @action(label='Take')
    def take(self, steal=False, set_open=False):
        action, pp = ('Steal', 'stolen') if steal else ('Take', 'taken')

        params = {'Action': action, 'id': self._ticket}
        if set_open:
            params['Status'] = 'open'
        response = self._request(params)

        if response.result == RTResult.USER_ALREADY_OWNS_TICKET:
            self._notify("It's already yours!",
                         "This ticket already belongs to you.",
                         gtk.STOCK_DIALOG_WARNING, [self.show])
        elif response.result == RTResult.TICKET_NOT_UNOWNED:
            self._notify("Already taken",
                         'This ticket already belongs to %s' % saxutils.escape(response.owner),
                         gtk.STOCK_DIALOG_WARNING, [self.show, self.steal])
        elif response.result == RTResult.OWNER_CHANGED:
            self._notify(pp.title(), 'You have successfully %s this ticket' % pp,
                         gtk.STOCK_DIALOG_INFO, [self.show])
            return True

    @action(label='Take and set open')
    def take_and_set_open(self):
        return self.take(set_open=True)

    @action(label='Steal')
    def steal(self):
        return self.take(steal=True)

    @action(label='Give')
    def give(self, new_owner=None):
        if not new_owner:
            try:
                new_owner = self._ask_question('Give ticket to…',
                                               'Enter the username of the new owner.',
                                               'Username:')
            except ValueError:
                return

        response = self._request({'Owner': new_owner, 'id': self._ticket})

        if response.result == RTResult.CANT_REASSIGN:
            self._notify("Couldn't change owner",
                         "This ticket belongs to %s, not you.%s" % (
                             saxutils.escape(response.owner),
                             ' Try stealing it first.' if 'actions' not in self._notify.caps else ''),
                         gtk.STOCK_DIALOG_WARNING, [self.show, self.steal_and_give(new_owner=new_owner, partial=True)])
        elif response.result == RTResult.OWNER_CHANGED:
            self._notify('Owner changed',
                         'This ticket now belongs to %s.' % saxutils.escape(response.owner),
                         gtk.STOCK_DIALOG_INFO, [self.show])
        elif response.result == RTResult.NO_SUCH_USER:
            self._notify('No such user',
                         "The ticket's owner wasn't changed as the specified user doesn't exist.",
                         gtk.STOCK_DIALOG_WARNING, [self.show, self.give_again])

    @action(label='Try again')
    def give_again(self):
        return self.give()

    @action(label='Steal and give')
    def steal_and_give(self, new_owner):
        return self.steal() and self.give(new_owner=new_owner)

    @action(label='Change queue')
    def change_queue(self, new_queue=None):
        if not new_queue:
            try:
                new_queue = self._ask_question('Change queue…',
                                               'Enter the name of the queue to which this ticket should be moved.',
                                               'Queue name:')
            except ValueError:
                return
        response = self._request({'Queue': new_queue, 'id': self._ticket})
        if response.result == RTResult.NO_SUCH_QUEUE:
            self._notify('No such queue',
                         "The ticket could not be moved as the given queue doesn't exist.",
                         gtk.STOCK_DIALOG_WARNING, [self.show, self.change_queue_again])
        else:
            self._notify('Queue changed',
                         'The ticket was successfully moved into the <i>%s</i> queue.' % new_queue,
                         gtk.STOCK_DIALOG_INFO, [self.show])
            return True

    @action(label='Try again')
    def change_queue_again(self):
        return self.change_queue()

    @action(label='Change status')
    def change_status(self, new_status=None):
        response = self._request({'Status': new_status, 'id': self._ticket})
        self._notify('Status changed',
                     'This ticket now has status <i>%s</i>.' % new_status,
                     gtk.STOCK_DIALOG_INFO, [self.show])

if __name__ == '__main__':
    pynotify.init(APPLICATION_NAME)
    rt_helper = RTHelper()
    gtk.main()

