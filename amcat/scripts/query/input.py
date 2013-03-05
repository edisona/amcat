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
Input Script for the Query Framework. The input script retrieves a
(filtered) list of articles (rows) with selected fields
(columns). This information is gathered and combined from different
sources (database, solr, coding tables) using FieldProviders.

The get_options_form should be called with a list of sets in order to
determine the fields that can be used (depending whether the sets are
indexed etc.)
"""

from __future__ import unicode_literals, print_function, absolute_import
from amcat.scripts.script import Script
from django import forms
from amcat.models import ArticleSet, Article

from amcat.scripts.query.articlemetafieldprovider import ArticleMetaFieldProvider
from amcat.scripts.query.solrfieldprovider import SolrFieldProvider
from amcat.scripts.query.fieldprovider import InputTable

FIELD_PROVIDERS = [ArticleMetaFieldProvider, SolrFieldProvider]
            
class QueryInputForm(forms.Form):
    articlesets = forms.ModelMultipleChoiceField(queryset=ArticleSet.objects.all())

    def __init__(self, *args, **kargs):
        project = kargs.pop('project', None)
        super(QueryInputForm, self).__init__(*args, **kargs)
        if project:
            self.fields['articlesets'].queryset = project.all_articlesets()

        sets = self.data.get('articlesets')
        if sets:
            for key, field in QueryInput.get_form_fields(sets):
                self.fields[key] = field

        if list(self.data.keys()) == ['articlesets']:
            self.is_bound = False
            self.fields['articlesets'].initial = sets
            
    def clean(self):
        cleaned_data = super(QueryInputForm, self).clean()
        cleaned_data = QueryInput.clean_form(cleaned_data)
        return cleaned_data

class QueryInput(Script):
    options_form = QueryInputForm
    
    @classmethod
    def get_form_fields(cls, sets):
        """
        Return the form with filter values specified for this project/sets. The form consists
        of the forms fields of the field providers, plus a choice field for the output fields.
        @return: a sequence of key, form field pairs
        """
        fieldnames = []
        for provider in FIELD_PROVIDERS:
            for label, field in provider.get_filter_fields(sets):
                yield label, field
                for fieldname in provider.get_output_fields(sets):
                    if fieldname not in fieldnames:
                        fieldnames.append(fieldname)
                
        yield "Columns", forms.MultipleChoiceField(choices=[(f,f) for f in fieldnames])

    @classmethod
    def clean_form(cls, cleaned_data):
        """Perform additional cleaning on the (validated) form"""
        for provider in FIELD_PROVIDERS:
            provider.clean_form(cleaned_data)
        return cleaned_data

    def run(self):
        """
        Collect the needed information

        Start by making a queryset of the articles in the selected sets, and then
        ask the field providers to add filters. 
        """
        columns = self.options.pop("Columns")
        providers = [provider(self.options, columns) for provider in FIELD_PROVIDERS]
        qs = Article.objects.filter(articlesets_set__in=self.options['articlesets'])
        table = InputTable(qs)
        for provider in providers:
            provider.filter(table)
        for provider in providers:
            provider.add_columns(table)
        return table

###########################################################################
#                          U N I T   T E S T S                            #
###########################################################################

from amcat.tools import amcattest

class TestInput(amcattest.PolicyTestCase):
    def setUp(self):
        self.p = amcattest.create_test_project()
        self.indexed_set, self.unindexed_set, self.coding_set = [amcattest.create_test_set(project=self.p, articles=5+i) for i in range(3)]
        self.all_sets = (self.indexed_set, self.unindexed_set, self.coding_set)
        for s in self.all_sets:
            s.indexed = s == self.indexed_set
            s.index_dirty = False
            s.save()
        self.job = amcattest.create_test_job(project=self.p, articleset=self.coding_set)
    
    def test_articlemeta(self):
        a1, a2, a3 = self.indexed_set.articles.all()[:3]
        q = QueryInput(articlesets = [self.indexed_set.id], Columns=["Section", "Date"], Medium=[a1.medium_id, a2.medium_id])
        result = list(q.run().to_list())
        self.assertEqual(len(result), 2)
        self.assertEqual({r.Date for r in result}, {a1.date, a2.date})
        
