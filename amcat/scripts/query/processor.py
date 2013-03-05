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
Processor Scripts for the Query Framework.

In principle, a processor takes the result of an input script and
returns useful output. The processor is responsible for selecting the
fields of the input script to use.

An example processor is a tabulator. If the user selects the 'display
as table' (or graph) option, the data needs to be tabulated. For this,
the user selects the fields to be used on the horizontal and vertical
axes and the information to be used in the cells. In the case of solr
or coding data, the tabulation is doing as a (in-python) stream
operation. For db data, the tabulation is done by converting the
queryset of the db source into an aggregate queryset. The result of
tabulation is a 'matrix': a table with (generally limited) rows and
columns drawn from the selected fields and numeric cell values.
"""

from amcat.scripts.script import Script
from django import forms
from django.core import validators
import csv
from amcat.tools.table import table3

class TableField(forms.FileField):
    """
    Field for a table input (deserialized from csv, other formats to be added)
    Allow a Table object to be passed in directly as well to allow for shortcuts
    """
    def __init__(self, *args, **kargs):
        self.format = kargs.pop('format', 'csv')
        super(TableField, self).__init__(*args, **kargs)
        
    def to_python(self, data):
        if data in validators.EMPTY_VALUES:
            return None
        if isinstance(data, table3.Table): 
            return data # no processing needed
        else:
            r = csv.reader(data)
            colnames = r.next()
            return table3.ListTable(r, colnames)
    


class Processor(Script):
    """
    Base class for scripts that can process query input results.
    The script 
    """

    class options_form(forms.Form):
        input_table = TableField()
    

class Tabulator(Processor):
    """Stream tabulator for tabulating a list"""
    
    @classmethod
    def get_options_form(cls, output_fields):
        class CustomOptionsForm(Processor.options_form):
            def __init__(self, *args, **kargs):
                Processor.options_form.__init__(self, *args, **kargs)
                for key, field in cls.get_extra_fields(output_fields):
                    self.fields[key] = field
        return CustomOptionsForm

    @classmethod
    def get_extra_fields(cls, output_fields):
        yield 'Row', forms.ChoiceField(choices=[(f,f) for f in output_fields])
        yield 'Column', forms.ChoiceField(choices=[(f,f) for f in output_fields])

    @classmethod
    def select_output_columns(cls, options):
        return options['Row'], options['Column']
    
    def _run(self, input_table, Row, Column):
        row_col, col_col = None, None
        for col in input_table.getColumns():
            if str(col) == Row: row_col = col
            if str(col) == Column: col_col = col

        # TODO: check whether both columns are QuerySet column, 
        #       and use a aggregate query instead of in-python aggregation
        return stream_tabulate(input_table, row_col, col_col)

def stream_tabulate(table, row_column, col_column):
    """
    Do a stream tabulation (currently only count) of the table
    @return: a table with the found values of row and col columns in the rows and columns,
             and the counts in the cell values
    """
    result = {}
    rows, cols = set(), set()
    for row in table.getRows():
        row_val = table.getValue(row, row_column)
        col_val = table.getValue(row, col_column)
        rows.add(row_val)
        cols.add(col_val)
        result[row_val, col_val] = result.get((row_val, col_val), 0) + 1
    return table3.DictTable(data=result, rows=rows, cols=cols)
    
###########################################################################
#                          U N I T   T E S T S                            #
###########################################################################

from amcat.tools import amcattest

class TestTableField(amcattest.PolicyTestCase):
    class TestForm(forms.Form):
        table = TableField()

    def test_deserialize(self):
        """can the table field deserialize a csv file?"""
        import StringIO
        table = StringIO.StringIO("a,b\n1,2\n3,4")
        f = self.TestForm(files=dict(table=table))
        self.assertEqual(f.is_valid(), True)
        result = f.cleaned_data['table']
        self.assertEqual([str(f) for f in result.getColumns()], ["a","b"])
        self.assertEqual(len(list(result.to_list())), 2)

    def test_deserialize(self):
        """can the table field handle a table object?"""
        table = table3.ListTable([(1,2), (3,4)], ["a", "b"])
        f = self.TestForm(files=dict(table=table))
        self.assertEqual(f.is_valid(), True)
        result = f.cleaned_data['table']
        self.assertEqual([str(f) for f in result.getColumns()], ["a","b"])
        self.assertEqual(len(list(result.to_list())), 2)


class TestTabulator(amcattest.PolicyTestCase):
    def test_tabulate(self):
        table = table3.ListTable([(1,20, 300), (1,30, 400), (2, 20, 500)], ["a", "b", "c"])
        form = Tabulator.get_options_form(output_fields = ["a","b","c"])
        form = form(data=dict(Row="a", Column="b"), files=dict(input_table=table))
        tabulator = Tabulator(form)
        result = tabulator.run()
        self.assertEqual(sorted(result.getRows()), [1, 2])
        self.assertEqual(sorted(result.getColumns()), [20, 30])
        self.assertEqual(result.data[1, 20], 1)
        #print(result.output(rownames=True))
