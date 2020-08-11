#!/usr/bin/python
# -*- coding: utf-8 -*-

print('Content-type: text/html\n\n')

import cgi

form = cgi.FieldStorage()

username = form.getvalue('username')

print(username)