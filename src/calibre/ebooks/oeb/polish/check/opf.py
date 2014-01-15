#!/usr/bin/env python
# vim:fileencoding=utf-8
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__ = 'GPL v3'
__copyright__ = '2014, Kovid Goyal <kovid at kovidgoyal.net>'

from calibre import prepare_string_for_xml as xml
from calibre.ebooks.oeb.polish.check.base import BaseError, WARN

class MissingSection(BaseError):

    def __init__(self, name, section_name):
        BaseError.__init__(self, _('The <%s> section is missing from the OPF') % section_name, name)
        self.HELP = xml(_(
            'The <%s> section is required in the OPF file. You have to create one.') % section_name)

class IncorrectIdref(BaseError):

    def __init__(self, name, idref, lnum):
        BaseError.__init__(self, _('idref="%s" points to unknown id') % idref, name, lnum)
        self.HELP = xml(_(
            'The idref="%s" points to an id that does not exist in the OPF') % idref)

class NonLinearItems(BaseError):

    level = WARN
    has_multiple_locations = True

    HELP = xml(_('There are items marked as non-linear in the <spine>.'
                 ' These will be displayed in random order by different ebook readers.'
                 ' Some will ignore the non-linear attribute, some will display'
                 ' them at the end or the beginning of the book and some will'
                 ' fail to display them at all. Instead of using non-linear items'
                 ' simply place the items in the order you want them to be displayed.'))

    INDIVIDUAL_FIX = _('Mark all non-linear items as linear')

    def __init__(self, name, locs):
        BaseError.__init__(self, _('Non-linear items in the spine'), name)
        self.all_locations = [(name, x, None) for x in locs]

    def __call__(self, container):
        [elem.attrib.pop('linear') for elem in container.opf_xpath('//opf:spine/opf:itemref[@linear]')]
        container.dirty(container.opf_name)
        return True

def check_opf(container):
    errors = []

    for tag in ('metadata', 'manifest', 'spine'):
        if not container.opf_xpath('//opf:' + tag):
            errors.append(MissingSection(container.opf_name, tag))

    all_ids = set(container.opf_xpath('//*/@id'))
    for elem in container.opf_xpath('//*[@idref]'):
        if elem.get('idref') not in all_ids:
            errors.append(IncorrectIdref(container.opf_name, elem.get('idref'), elem.sourceline))

    nl_items = [elem.sourceline for elem in container.opf_xpath('//opf:spine/opf:itemref[@linear="no"]')]
    if nl_items:
        errors.append(NonLinearItems(container.opf_name, nl_items))

    return errors
