# -*- coding: utf-8 -*-

from __future__ import absolute_import
from . import *
from talon import email_splitter


def test_split_email():
    msg = """From: Mr. X
    Date: 24 February 2016
    To: Mr. Y
    Subject: Hi
    Attachments: none
    Goodbye.
    From: Mr. Y
    To: Mr. X
    Date: 24 February 2016
    Subject: Hi
    Attachments: none

    Hello.

        On 24th February 2016 at 09.32am Conal Wrote:

        Hey!

        On Mon, 2016-10-03 at 09:45 -0600, Stangel, Dan wrote:
        > Mohan,
        >
        > We have not yet migrated the systems.
        >
        > Dan
        >
        > > -----Original Message-----
        > > Date: Mon, 2 Apr 2012 17:44:22 +0400
        > > Subject: Test
        > > From: bob@xxx.mailgun.org
        > > To: xxx@gmail.com; xxx@hotmail.com; xxx@yahoo.com; xxx@aol.com; xxx@comcast.net; xxx@nyc.rr.com
        > >
        > > Hi
        > >
        > > > From: bob@xxx.mailgun.org
        > > > To: xxx@gmail.com; xxx@hotmail.com; xxx@yahoo.com; xxx@aol.com; xxx@comcast.net; xxx@nyc.rr.com
        > > > Date: Mon, 2 Apr 2012 17:44:22 +0400
        > > > Subject: Test
        > > > Hi
        > > >
        > >
        >
        >
"""
    expected_markers = "stttttstttteteteteesmmmmmmssmmmmmmsmmmmmmmm"
    markers = email_splitter.split_emails(msg)
    eq_(markers, expected_markers)
