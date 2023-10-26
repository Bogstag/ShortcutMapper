# -*- coding: utf-8 -*-
"""
This module provides functionality for processing HTML data.
"""

import codecs
import os
import re

from bs4 import BeautifulSoup

from shmaplib.intermediate import IntermediateShortcutData
from shmaplib.logger import getlog

log = getlog()


def _get_file_contents(source):
    """
    Reads the contents of the specified file and returns it as a string.

    Parameters:
        source (str): The path or filename of the file to read.

    Returns:
        str: The contents of the file as a string.

    """
    f = codecs.open(source, encoding='utf-8')
    contents = f.read()
    f.close()
    return contents


class AdobeDocsParser(object):
    """This parser scrapes shortcuts and contexts from an adobe shortcuts documentation html file,
    such as: http://helpx.adobe.com/en/photoshop/using/default-keyboard-shortcuts.html

    It assumes the main relevant data is contained in a wrapper div: 
        <div class="parsys main-pars">...</div>
    From the contents of this div, it can extract shortcut contexts, 
    shortcut names and keys for Windows and MacOS
    """

    def __init__(self, app_name):
        super(AdobeDocsParser, self).__init__()
        self.idata = IntermediateShortcutData(app_name)

    @staticmethod
    def _clean_text(text):
        text = text.replace('\n', ' ').strip(' ').replace('\xa0', ' ')
        # Remove stuff within braces
        text = re.sub(r"([\(]).*?([\)])", "", text)
        # Remove meta-data tags
        text = text.replace('†', '').replace('‡', '').strip('*')

        return text.strip(' ')


def parse(self, file_path):
    """
    Parse the HTML source file and extract shortcuts.

    Args:
        file_path (str): Path of the source file.

    Returns:
        IData: Instance of IData containing the parsed shortcuts.
    """
    if not os.path.exists(file_path):
        log.error("Source file '%s' does not exist", file_path)
        return None

    # Use BeautifulSoup to parse the html document
    doc = BeautifulSoup(_get_file_contents(file_path))
    main_div = doc.find("div", class_="parsys main-pars")
    if main_div is None:
        main_div = doc.find("div", id="main")
    parbase_sections = main_div.find_all(
        "div", class_="parbase")  # type: ignore

    # Iterate sections (headers are contexts, tables contain the shortcuts)
    context_name = None
    for section in parbase_sections:
        # This section is a header, the only relevant information here is the context
        if 'header' in section['class']:
            header_element = section.find('h2')
            context_name = str(header_element.contents[0]).replace(
                '\n', ' ').strip(' ')

        # This is a section containing the shortcuts table
        elif 'table' in section['class']:
            table_rows = section.find('tbody').find_all('tr')

            for row in table_rows:
                table_columns = row.find_all("td")
                if len(table_columns) != 3:
                    continue

                shortcut_name = self._clean_text(table_columns[0].get_text())
                keys_win = self._clean_text(table_columns[1].get_text())
                keys_mac = self._clean_text(table_columns[2].get_text())

                self.idata.add_shortcut(
                    context_name, shortcut_name, keys_win, keys_mac)

    return self.idata


class AdobeSummaryParser(object):
    """This parser scrapes shortcuts and contexts from an adobe summary export. 
    This file is exported from photoshop's Edit shortcuts dialog."""

    def __init__(self, app_name):
        super(AdobeSummaryParser, self).__init__()
        self.idata = IntermediateShortcutData(app_name)

    def parse(self, source_filepath, platform_type):
        """
        Parses an HTML document, extracts shortcuts from tables, and adds them to the idata object.

        Args:
            source_filepath (str): The path to the HTML document to be parsed.
            platform_type (str): The type of platform ('windows' or 'mac').

        Returns:
            idata (object): The idata object with added shortcuts.
        """
        assert platform_type in ["windows",
                                 "mac"], "Platform must be 'windows' or 'mac'"

        if not os.path.exists(source_filepath):
            log.error("Source file '%s' does not exist", source_filepath)
            return

        # Use BeautifulSoup to parse the html document
        doc = BeautifulSoup(_get_file_contents(source_filepath))
        tables = doc.find_all('table')

        for table in tables:
            parent_categories = []
            prev_was_category = False
            indentation = None

            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')

                # Check for category
                if len(cols) == 1:
                    if len(parent_categories) == 0:
                        parent_categories = parent_categories[:len(
                            parent_categories)-1]
                    if len(cols[0]):
                        parent_categories.append(cols[0].text + '>')
                    continue

                spacers = row.find_all('td', attrs={'width': '40'})
                shortcutcols = row.find_all(
                    'td', attrs={'class': 'shortcutcols'})

                # Handle indentation
                if not indentation:
                    indentation = len(spacers)
                if len(spacers) < indentation:
                    if prev_was_category and len(spacers) == indentation:
                        parent_categories = parent_categories[:len(
                            parent_categories)-1]
                indentation = len(spacers)

                # Skip if there are no shortcuts in this row
                if not shortcutcols:
                    # Check if it is a parent menu item '>'
                    for col in cols:
                        if '>' in col.text:
                            category = col.text
                            parent_categories.append(category)
                            prev_was_category = True
                    continue
                prev_was_category = False

                # Find the name and shortcut text

                # Find the name and shortcut text
                name = None
                keys = None
                for col in shortcutcols:
                    if col.text:
                        if name is None:
                            name = col.text.replace('...', '')
                            continue

                        # Check if content is &nbsp;
                        if col.text == '\xa0':
                            continue

                        # Shortcut + removing <br>'s
                        keys = ' or '.join(col.findAll(text=True))

                        # No need to continue, we found the the shortcuts
                        break

                if not keys:
                    continue

                # It's a shortcut, but is it set?
                full_name = ''.join(parent_categories)
                if name:
                    full_name += name

                if platform_type == 'windows':
                    self.idata.add_shortcut("Application", full_name, keys, "")
                else:
                    self.idata.add_shortcut("Application", full_name, "", keys)

        return self.idata
