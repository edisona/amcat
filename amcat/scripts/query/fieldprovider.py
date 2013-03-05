###########################################################################
#          (C) Vrije Universiteit, Amsterdam (the Netherlands)            #
#                                                                         #
# This file is part of AmCAT - The Amsterdam Content Analysis Toolkit     #
#                                                                         #
# AmCAT is free software: you can redistribute it and/or modify it under  #
# the terms of the GNU Affero General Public License as published by the  #
# Free Software Foundation, either version 3 of the License, or (at your  #
# option) any later version.                                              #
#                                                                         #
# AmCAT is distributed in the hope that it will be useful, but WITHOUT    #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or   #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public     #
# License for more details.                                               #
#                                                                         #
# You should have received a copy of the GNU Affero General Public        #
# License along with AmCAT.  If not, see <http://www.gnu.org/licenses/>.  #
###########################################################################

"""
Field providers provide the fields used in the input script.
"""

from amcat.tools.table.table3 import ObjectTable

class InputTable(ObjectTable):
    """
    A ObjectTable based on a queryset.
    The rows are the output of values_list, see the get_field_value(row, field) method.
    Columns should be added by the field providers based on the output fields selected by the user
    The queryset will not be instantiated until the call the getRows, so the queryset
    and selected_columns fields can be modified safely until the getRows call.
    Since getRows yields a generator it should be called only once.
    """
    def __init__(self, queryset):
        super(InputTable, self).__init__()
        self.queryset = queryset
        self.selected_columns = {"id"}
    def getRows(self):
        self.selected_columns = list(self.selected_columns)
        return self.queryset.values_list(*self.selected_columns)
    def get_column_value(self, row, column):
        """
        Get the value of the given row for the given column
        @param column: one of the column names in self.selected_columns
        """
        return row[self.selected_columns.index(column)]

class FieldProvider(object):
    """
    Class that represents a source of data for the query/input script.
    Each field provider represents a 'class' of data (articlemeta, solr, coding) that can be filtered
    and retrieved together. 
    A field provider has class method that can be called before the query is made by the user, in order
    to build the form with the possible filter and output fields. After instantiating the provider
    with the filled out query form, it has methods to filter the data and provide output columns
    """
    
    @classmethod
    def get_filter_fields(cls, articleset_ids):
        """
        Class method to provide the filter fields provided by this provider,
        possibly filtered using the article sets
        @return: a sequence of django form field objects
        """
        raise NotImplementedError()

    @classmethod
    def get_output_fields(cls, articleset_ids):
        """
        Class method to provide the selectable output fields provided by this provider,
        possibly filtered using the article sets
        @return: a sequence of field names (strings) 
        """
        raise NotImplementedError()

    @classmethod
    def clean_form(self, cleaned_data):
        """
        Optionally clean the query form's cleaned_data, or throw a ValidationError
        """
        pass
    
    def __init__(self, cleaned_data, output_fields):
        """
        Initialize a field provider with filled in filter fields and selected output columns.
        All data is given now to allow optimizations in the filter/add_columns steps.
        @param cleaned_data: the cleaned data of the form
        @param columns: a list of output fields (columns) that should be included in the data
        """
        self.cleaned_data = cleaned_data
        self.output_fields = output_fields

    def filter(self, input_table):
        """
        Filter the input data based on the instantiated filter fields provided by this provider.
        This method will also be called if none of the form fields yielded by this provider are filled in,
        in which case the original queryset should probably be returned.
        If desired, the provider can also add fields to the table's selected_columns in this method.
        @param table: An InputTable whose queryset and selected_columns fields can be adjusted. 
        """
        raise NotImplementedError()

    def add_columns(self, table):
        """
        Add columns to the given InputTable to provide the data for the selected output_fields
        """
        raise NotImplementedError()

    

