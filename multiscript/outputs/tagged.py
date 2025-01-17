
from enum import Enum, auto
import logging
from typing import Text
from multiscript.bible.content import BibleStreamHandler

from multiscript.outputs.fileset import FileSetOutput
from multiscript.plan.symbols import column_symbols


class Tags(Enum):
    ALL_VERS_USER_LANG      =   "[MSC_ALL_VERS_USER_LANG]"      # Expands to a list of all the versions'
                                                                #   languages (user labels)
    UNIQUE_VERS_USER_LANG   =   "[MSC_UNIQUE_VERS_USER_LANG]"   # Expands to a list of versions languages (user labels)
                                                                #   for unique versions in the plan (i.e. ignores
                                                                #   columns with just one version in them)
    TWO_PLUS_VERS_USER_LANG =   "[MSC_2+_VERS_USER_LANG]"       # Deprecated. Expands to a list of all the versions'
                                                                #   languages (user labels), except the first
    VER_USER_LANG           =   "[MSC_VER_USER_LANG_{0}]"       # Expands to one version's lanaguage (user label).
                                                                #   The parameter is the column symbol (e.g. A,B,C)
    ALL_TABLES              =   "[MSC_ALL_TABLES]"              # For each Bible group, generates a PASSAGE_GROUP
                                                                #   header, followed by a table containing the Bible
                                                                #   TEXTs. The first table in the doc includes an extra
                                                                #   row at the top containing the VER_NAMEs.
    PASSAGE_GROUP           =   "[MSC_PASSAGE_GROUP_{0}]"       # Expands to the Bible passage reference for
                                                                #   the entire group of passages. The paramter is the
                                                                #   group number (starting from 1).
    PASSAGE                 =   "[MSC_PASSAGE_{0}]"             # Expands to a single Bible passage reference. The
                                                                #   parameter is the passage number (starting from 1).
    VER_NAME                =   "[MSC_VER_NAME_{0}]"            # Expands to the version's name
                                                                #   The parameter is the column symbol (e.g. A,B,C)
    TEXT                    =   "[MSC_TEXT_{0}{1}]"             # Expands to the Bible text. The parameters are
                                                                #   (in order) the passage number, and the column
                                                                #   symbol (e.g. 1A)
    TEXT_JOIN               =   "[MSC_TEXT_JOIN]"               # Expands to the join indicator between group passages
    COPYRIGHT               =   "[MSC_COPYRIGHT_{0}]"           # Expands to the copyright text for one version
                                                                #   The parameter is the column symbol (e.g. A,B,C)


class TaggedOutput(FileSetOutput):
    '''An abstract FileSetOutput that replaces a standard set of tags with Bible content.
    '''
    def __init__(self, plugin):
        super().__init__(plugin)

    def expand_base_template(self, runner, document):
        '''Overrides FileSetOutput.expand_base_template(). Called if the newly loaded document is
        actually the base template. Handles tags in the base template that expand to other tags
        (e.g. ALL_TABLES), as well as adding COPYRIGHT tags if they are not yet present in the
        document.
        '''
        # Expand Tags.ALL_TABLES
        tag = Tags.ALL_TABLES.value        
        cursor = self.replace_tag_with_cursor(document, tag)
        if cursor is not None:
            group_index = 0     # Counts through each group.
            contents_index = 0  # Counts through each passage ignoring which group it's in.
            for range_group in runner.bible_ranges.groups:
                tag_text = Tags.PASSAGE_GROUP.value.format(group_index + 1)
                is_first = (group_index == 0)
                self.insert_passage_group_tag(runner, document, cursor, is_first, tag_text)

                table_text_array = [] # List of rows, each of which is a list of column text                
                # For the first table, include the MS_VER_NAME tags
                if is_first:
                    table_text_row = []
                    for column_index in range(len(runner.version_cols)):
                        table_text_row.append(Tags.VER_NAME.value.format(column_symbols[column_index]))
                    table_text_array.append(table_text_row)

                table_text_row = ["" for column_index in range(len(runner.version_cols))]
                range_index = 0
                for bible_range in range_group:
                    # Include MS_TEXT tags for the bible content body
                    for column_index in range(len(runner.version_cols)):
                        table_text_row[column_index] += Tags.TEXT.value.format(contents_index + 1,
                                                                               column_symbols[column_index])
                        if range_index < (len(range_group) -1):
                            table_text_row[column_index] += "\n" + Tags.TEXT_JOIN.value + "\n"
                        
                    range_index += 1
                    contents_index += 1

                table_text_array.append(table_text_row)
                self.insert_passage_group_table(runner, document, cursor, is_first, table_text_array)
                group_index += 1

        # Check if all copyright tags are present
        all_copyright_tags_found = True
        for column_index in range(len(runner.version_cols)):
            tag = "[MS_COPYRIGHT_{0}]".format(column_symbols[column_index])
            all_copyright_tags_found = self.text_found(document, tag)
            if not all_copyright_tags_found:
                break
        
        # Insert table of copyright tags if necessary
        if not all_copyright_tags_found:
            table_text_row = []
            for column_index in range(len(runner.version_cols)):
                table_text_row.append(Tags.COPYRIGHT.value.format(column_symbols[column_index]))
            # If cursor is not None, we've already expanded an MS_ALL_TABLES tag, so insert the
            # copyright table should be inserted at the current cursor location.
            # We didn't expand an MS_ALL_TABLES tag, so cursor is None, and the copyright table
            # should be inserted the end of the document.
            self.insert_copyright_table(runner, document, cursor, [table_text_row])

    def begin_fill_document(self, runner, version_combo, document, is_template):
        '''Overrides FileSetOutput.begin_file_document(). Called immediately before fill_document().
        We expand tags that relate to the whole document (e.g. ALL_VERS_USER_LANG, PASSAGE_GROUP,
        COPYRIGHT), rather than individual version combos.
        '''
        if not is_template:
            # These tags can't be completed if we're building a template, as we won't know all the versions
            tag = Tags.ALL_VERS_USER_LANG.value
            versions = [element.version for element in version_combo if element.version is not None]
            replace_text = ", ".join([version.user_labels.lang for version in versions])
            self.replace_tag_directly(document, tag, replace_text)

            tag = Tags.UNIQUE_VERS_USER_LANG.value
            versions = [element.version for element in version_combo if element.version is not None \
                                                                  and len(element.version_column) > 1]
            replace_text = ", ".join([version.user_labels.lang for version in versions])
            self.replace_tag_directly(document, tag, replace_text)

            tag = Tags.TWO_PLUS_VERS_USER_LANG.value
            versions = [element.version for element in version_combo if element.version is not None \
                                                         and element.version_column.symbol_index > 0]
            replace_text = ", ".join([version.user_labels.lang for version in versions])
            self.replace_tag_directly(document, tag, replace_text)
        
        # Fill in grouped passage tags.
        for group_index in range(len(runner.bible_ranges.groups)):
            tag = Tags.PASSAGE_GROUP.value.format(group_index + 1)
            range_group = runner.bible_ranges.groups[group_index]
            self.replace_tag_directly(document, tag, range_group.string(nobook=True, showgroups=True))

        # Fill in copyright tags
        versions = [element.version if element.version is not None else None for element in version_combo]
        bible_contents = [runner.bible_contents[version][0] if version is not None else None for version in versions]
        for column_index in range(len(bible_contents)):
            bible_content = bible_contents[column_index]
            if bible_content is not None:
                tag = Tags.COPYRIGHT.value.format(column_symbols[column_index])
                cursor = self.replace_tag_with_cursor(document, tag)
                if cursor is not None:
                    self.format_copyright_text_tag(document, bible_content, cursor)
                    cursor.add_text(bible_content.copyright_text)

    def fill_bible_content(self, runner, document, contents_index, column_symbol, bible_content):
        '''Overrides FileSetOutput.fill_bible_content(). Inserts the specified bible_content into the document,
        at the specified contents_index and column_symbol.
        '''
        self.expand_direct_tags(runner, document, contents_index, column_symbol, bible_content)
        self.expand_cursor_tags(runner, document, contents_index, column_symbol, bible_content)

    def expand_direct_tags(self, runner, document, contents_index, column_symbol, bible_content):
        '''Expands direct tags with data from bible_content. Direct tags are those
        that can be replaced as simple strings without the need for a document cursor.
        '''
        #
        # TODO: Add more tags that can be used in the template
        #
        tag = Tags.PASSAGE.value.format(contents_index + 1)
        self.replace_tag_directly(document, tag, str(bible_content.bible_range))

        tag = Tags.VER_USER_LANG.value.format(column_symbol)
        self.replace_tag_directly(document, tag, str(bible_content.bible_version.user_labels.lang))

        tag = Tags.VER_NAME.value.format(column_symbol)
        self.replace_tag_directly(document, tag, str(bible_content.bible_version.name))

    def expand_cursor_tags(self, runner, document, contents_index, column_symbol, bible_content):
        '''Expands cursor tags with data from bible_content. Cursor tags are those
        that are more complex replacement operations that require the use of a document cursor.
        '''
        tag = Tags.TEXT.value.format(contents_index + 1, column_symbol)
        cursor = self.replace_tag_with_cursor(document, tag)
        if cursor is not None:
            self.format_bible_text_tag(document, contents_index, column_symbol, bible_content, cursor)
            bible_stream_handler = self.new_bible_stream_handler(runner, cursor)
            bible_content.body.copyStreamTo(bible_stream_handler)

    def replace_tag_directly(self, document, tag_text, replacement_text):
        '''Abstract method. Subclasses must override to search document for tag_text, and replace it
        with replacement_text. Any surrounding text in the paragraph should be left untouched.
        If tag_text is not found, the document should not be modified.
        '''
        pass

    def replace_tag_with_cursor(self, document, tag_text):
        '''Abstract method. Subclasses must override to search document for tag_text, remove it and
        return a subclass of TaggedDocCursor point to the paragraph. If not tag_text is not found,
        this method should return None.
        '''

    def new_bible_stream_handler(self, runner, cursor):
        '''Abstract method. It should return a BibleStreamHander.'''
        return BibleStreamHandler()

    def text_found(self, document, search_text):
        '''Abstract method. Subclasses must override to search document for search_text, and return
        True if found, else False.
        '''
        pass

    def insert_passage_group_tag(self, runner, document, cursor, is_first, tag_text):
        '''Abstract method. Called when expanding base template tags. Subclasses must override to
        format the document for a passage group header, and then actually insert the tag_text.

        first_group is True if this is the first passage group header being inserted.
        '''
        pass

    def insert_passage_group_table(self, runner, document, cursor, is_first, table_text_array):
        '''Abstract method. Called when expanding base template tags. Subclasses must override to
        insert a passage group table at the current cursor point and then insert the text in
        table_text_array into that table, adding any formatting necessary.
        '''
    
    def insert_copyright_table(self, runner, document, cursor, table_text_array):
        '''Abstract method. Called when expanding base template tags. Subclasses must override.
        If cursor is not None, subclasses should insert a copyright table at the current cursor
        point. If cursor is None, subclasses should insert a copyright table at the end of the
        document.
        '''
        pass
 
    def format_bible_text_tag(self, document, contents_index, column_symbol, bible_content, cursor):
        '''Abstract method. Subclasses can override to perform formatting needed prior to Bible content
        being inserted. The supplied cursor will be at the insertion point.
        '''
        pass

    def format_copyright_text_tag(self, document, bible_content, cursor):
        '''Perform any formatting needed prior to copyright text being inserted. The supplied
        cursor will be at the insertion point.
        '''
        pass


class TaggedDocCursor:
    '''A abstract cursor for tracking an insertion point in a document, along with abstract
    methods for adding basic content. Subclasses of TaggedOuput should also subclass this class.
    '''
    def __init__(self, document):
        self.document = document

    def add_new_para(self, text=None, *args, **kwargs):
        '''Add a new paragraph to the document, with optional text.
        '''
        pass

    def add_new_run(self, text=None, *args, **kwargs):
        '''Add a new run to the document, with optional text. For formatted documents, a run is a string
        of text with the same formatting. For unformatted documents, it's just plain text.

        Extra args and kwargs are allowed for extra document options.
        '''
        pass

    def add_text(self, text):
        '''Add text to the document (in the current run).
        '''
        pass
