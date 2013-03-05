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
Query Script for the Query framework

A query combines an input, processor, and (in the future) output script.
"""

from amcat.scripts.script import Script
from amcat.scripts.query import input, processor
from django import forms
from django.core import validators
import csv
from amcat.tools.table import table3

PROCESSORS = {'Graph/Table' : processor.Tabulator}

class QueryForm(input.QueryInputForm):
    # TODO: if desired, dynamically determine this list based on available output fields
    processor = forms.ChoiceField(choices=[(k,k) for k in PROCESSORS.keys()])
    
    def __init__(self, *args, **kargs):
        super(QueryForm, self).__init__(*args, **kargs)
        # if we have columns and a processor, we can add the custom processor fields
        processor = PROCESSORS.get(self.data.get('processor'))
        if processor and 'Columns' in self.fields:
            columns = [k for (k,k) in self.fields['Columns'].choices]
            for key, field in processor.get_extra_fields(columns):
                self.fields[key] = field
            # remove columns field, will be filled in from the processor
            del self.fields['Columns']

class Query(Script):
    options_form = QueryForm

    
    def _run(self, processor, **options):
        """
        1. Ask the processor class for the output columns
        2. Execute the input script
        3. Execute the processor script
        """
        processor = PROCESSORS[processor]
        columns = processor.select_output_columns(options)

        self.bound_form.cleaned_data['Columns'] = columns
        input_script = input.QueryInput(self.bound_form)
        article_table = input_script.run()


        form = processor.get_options_form(columns)(data=self.bound_form.data, files=dict(input_table=article_table))
        result = processor(form).run()

        return result

        
#QueryForm(dict(articlesets=[2]))


        
