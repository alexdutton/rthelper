RT Helper documentation
=======================

The RT Helper widget is designed to interact with RT without the need for a web
browser. In most cases you'll select an RT ticket number from your mail client,
right-click on the icon, and select the task you want to perform. Shortly after
you'll receive a notification to tell you whether the action succeeded.

Supported platforms
-------------------

The widget currently only supports Linux desktops. It has been tested under
GNOME 2.30 and awesome. It depends on the GNOME keyring and requires support
for the freedesktop libnotify standard.

By default it is set up for use with the RT instance at Oxford University
Computing Services. However, you can change this by editing the RT_URL and
AUTHENTICATION variables near the top of the file. It supports standard RT
authentication and WebAuth (tested at the University of Oxford).

Selecting a ticket
------------------

The widget monitors the primary selection buffer¹ for things that look like RT
ticket numbers. When no number is present, the icon has a small cross in the
bottom-right corner; this will disappear to let you know when a ticket number
has been detected. It ignores any leading or trailing punctuation, and the
strings 'RT' and '#' before the number, so you don't need to be too careful
when selecting the number. This also allows you to double-click on a number to
select it in most contexts.

¹ In case you didn't know, the primary selection buffer is the one you paste
  from by middle-clicking. To add something to it, simply highlight a portion
  of text using the mouse.

Authentication
--------------

The first time you use the widget, it will ask you for your WebAuth username
and password. This is stored in your GNOME login keyring, which is encrypted
with your desktop password. You can remove your credentials later using
Seahorse (sometimes called 'Passwords and Encryption Keys' in the 'Accessories'
menu in GNOME).

Features
--------

Most of the actions are intuitive. Currently supported are:

 * Show
 * Take
 * Take and set open
 * Disown (i.e. give to 'Noboby in particular')
 * Give ticket to… (presents a dialog asking for a username)
 * Change queue… (presents a dialog asking for a queue name)
 * Punt… (asks for a queue name, then takes the ticket, moves the ticket to the
   given queue, and disowns it)
 * Set open
 * Quick resolve
 * Quick reject
 * Delete

These actions are effectively performed blind, so there are no options to
comment or correspond on a ticket as it could lead to duplicated or uninformed
communication.

Taking a ticket will fail if it has already been taken. In this case, the
notification will have a 'Steal' button. Other actions involving taking a
ticket (e.g. 'Give ticket to…') have similar fallbacks (e.g. 'Steal and give').
