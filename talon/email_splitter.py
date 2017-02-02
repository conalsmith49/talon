# -*- coding: utf-8 -*-

"""
The module's functions operate on message bodies trying to extract
original messages (without quoted messages)
"""

from __future__ import absolute_import
from talon.quotations import (preprocess, MAX_LINES_COUNT, RE_HEADER,
                              RE_FWD, SPLITTER_PATTERNS, SPLITTER_MAX_LINES,
                              is_splitter)
import regex as re
import logging

from talon.utils import (get_delimiter)


log = logging.getLogger(__name__)


QUOT_PATTERN = re.compile('^[ ]*>+ ?')


def split_emails(msg):
    """
    Given a message (which may consist of an email conversation thread with multiple emails), mark the lines to identify
     split lines, content lines and empty lines.

    Correct the split line markers inside header blocks. Header blocks are identified by the regular expression
    RE_HEADER.

    Return the corrected markers
    """
    delimiter = get_delimiter(msg)
    msg_body = preprocess(msg, delimiter)
    # don't process too long messages
    lines = msg_body.splitlines()[:MAX_LINES_COUNT]
    markers = mark_message_lines(lines)

    markers = _mark_quoted_email_splitlines(markers, lines)

    # we don't want splitlines in header blocks
    markers = _correct_splitlines_in_headers(markers, lines)

    return markers


def _mark_quoted_email_splitlines(markers, lines):
    """
    When there are headers indented with '>' characters, this method will attempt to identify if the header is a
    splitline header. If it is, then we mark it with 's' instead of leaving it as 'm' and return the new markers.
    """
    # Create a list of markers to easily alter specific characters
    markerlist = list(markers)
    for i, line in enumerate(lines):
        if markerlist[i] != 'm':
            continue
        for pattern in SPLITTER_PATTERNS:
            matcher = re.search(pattern, line)
            if matcher:
                markerlist[i] = 's'
                break

    return "".join(markerlist)


def _correct_splitlines_in_headers(markers, lines):
    """Corrects markers by removing splitlines deemed to be inside header blocks"""
    updated_markers = ""
    i = 0
    in_header_block = False

    for m in markers:
        # Only set in_header_block flag true when we hit an 's' and the line is a header.
        if m == 's':
            if not in_header_block:
                if bool(re.search(RE_HEADER, lines[i])):
                    in_header_block = True
            else:
                if QUOT_PATTERN.match(lines[i]):
                    m = 'm'
                else:
                    m = 't'

        # If the line is not a header line, set in_header_block false.
        if not bool(re.search(RE_HEADER, lines[i])):
            in_header_block = False

        # Add the marker to the new updated markers string.
        updated_markers += m
        i += 1

    return updated_markers


def mark_message_lines(lines):
    """Mark message lines with markers to distinguish quotation lines.

    Markers:

    * e - empty line
    * m - line that starts with quotation marker '>'
    * s - splitter line
    * t - presumably lines from the last message in the conversation

    >>> mark_message_lines(['answer', 'From: foo@bar.com', '', '> question'])
    'tsem'
    """
    markers = ['e' for _ in lines]
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            markers[i] = 'e'  # empty line
        elif QUOT_PATTERN.match(lines[i]):
            markers[i] = 'm'  # line with quotation marker
        elif RE_FWD.match(lines[i]):
            markers[i] = 'f'  # ---- Forwarded message ----
        else:
            # in case splitter is spread across several lines
            splitter = is_splitter('\n'.join(lines[i:i + SPLITTER_MAX_LINES]))

            if splitter:
                # append as many splitter markers as lines in splitter
                splitter_lines = splitter.group().splitlines()
                for j in range(len(splitter_lines)):
                    markers[i + j] = 's'

                # skip splitter lines
                i += len(splitter_lines) - 1
            else:
                # probably the line from the last message in the conversation
                markers[i] = 't'
        i += 1

    return ''.join(markers)
