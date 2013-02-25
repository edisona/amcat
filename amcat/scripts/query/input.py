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
Input Scripts for the Query Framework. An input script retrieves a
list of articles (or other units) and fields from a specific
information source, e.g. database, solr, or coding tables. All input
scripts are based on the 'abstract' QueryInput class. Apart from the
standard Script interface, a QueryInput has methods to provide
information about the script, e.g. which fields (columns) it can
yield and which sets are usable.
"""

from __future__ import unicode_literals, print_function, absolute_import
from amcat.scripts.script import Script
from django import forms
from amcat.scripts.forms import ModelMultipleChoiceFieldWithIdLabel
from amcat.models import Project, ArticleSet, Medium

class QueryInput(Script):
    """
    'Abstract' base class for QueryInput scripts. 
    """
    @classmethod
    def get_sets(cls, project):
        """Return the sets of the given project that are suitable as input for this script"""
        raise NotImplementedError()

    @classmethod
    def get_empty_form(cls, project, sets, **options):
        """Return the form with filter values specified for this project/sets"""
        raise NotImplementedError()

DATETYPES = {
    "all" : "All Dates",
    "on" : "On",
    "before" : "Before",
    "after" : "After",
    "between" : "Between",
}
    
class ArticleMetaForm(forms.Form):
    project = forms.ModelChoiceField(queryset=Project.objects.order_by('-pk')) 
    articlesets = ModelMultipleChoiceFieldWithIdLabel(queryset=ArticleSet.objects.none(), required=False)
    mediums = ModelMultipleChoiceFieldWithIdLabel(queryset=Medium.objects.none(), required=False)
    datetype = forms.ChoiceField(choices=DATETYPES.items(), initial='all')
    startDate = forms.DateField(input_formats=('%d-%m-%Y',), required=False)
    endDate = forms.DateField(input_formats=('%d-%m-%Y',), required=False)
    onDate = forms.DateField(input_formats=('%d-%m-%Y',), required=False)
    # queries will be added by clean(), that contains a list of SearchQuery objects
    
    def clean(self):
        # handle date ranges
        cleanedData = self.cleaned_data
        if cleanedData.get('datetype') in ('after', 'all') and 'endDate' in cleanedData:
            del cleanedData['endDate']
        if cleanedData.get('datetype') in ('before', 'all') and 'startDate' in cleanedData:
            del cleanedData['startDate']
        if cleanedData.get('datetype') == 'on':
            cleanedData['datetype'] = 'between'
            cleanedData['startDate'] = cleanedData['onDate'] 
            cleanedData['endDate'] = cleanedData['onDate'] + datetime.timedelta(1)
        # validate dates
        missingDateMsg = "Missing date"
        if 'endDate' in cleanedData and cleanedData['endDate'] == None: 
            self._errors["endDate"] = self.error_class([missingDateMsg])
            del cleanedData['endDate']
        if 'startDate' in cleanedData and cleanedData['startDate'] == None: 
            self._errors["startDate"] = self.error_class([missingDateMsg])
            del cleanedData['startDate']
        #todo: shouldn't we validate enddate > startdate etc?
        return cleanedData

    
class ArticleMetaInput(QueryInput):
    """QueryInput Script based on article meta data"""

    options_form = ArticleMetaForm
    
    @classmethod
    def get_sets(cls, project):
        return project.all_articlesets()
    
    @classmethod
    def get_empty_form(cls, project, sets, **options):
        f = cls.options_form()
        f.fields['project'].initial = project
        f.fields['project'].widget = forms.HiddenInput()
        f.fields['articlesets'].initial = sets
        #f.fields['articlesets'].queryset = cls.get_sets(project)
        f.fields['articlesets'].widget = forms.HiddenInput()

        f.fields['mediums'].queryset = Medium.objects.filter(article__articlesets_set__in=sets).distinct()

        
        return f
    
class SolrInput(QueryInput):
    """QueryInput Script based on solr full text index data"""
    @classmethod
    def get_sets(cls, project):
        """Use only sets that have been indexed"""
        return project.all_articlesets().filter(indexed=True, index_dirty=False)

class CodingInput(QueryInput):
    """QueryInput Script based on manually coded data"""
    @classmethod
    def get_sets(cls, project):
        """Use only sets that are used as a coding job"""
        return project.all_articlesets().filter(codingjob_set__isnull=False)

INPUT_SCRIPTS = [(unicode(s.__name__), s) for s in [ArticleMetaInput, SolrInput, CodingInput]]
    
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
        
        j = amcattest.create_test_job(project=self.p, articleset=self.coding_set)
    
    def test_get_sets(self):
        for (cls, sets) in [
            (ArticleMetaInput, self.all_sets),
            (SolrInput, {self.indexed_set}),
            (CodingInput, {self.coding_set}),
            ]:
            self.assertEqualsAsSets(cls.get_sets(self.p), sets)
        
    
