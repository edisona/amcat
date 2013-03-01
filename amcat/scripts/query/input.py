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
from amcat.scripts.query.field import article_field

class QueryInput(Script):
    """
    'Abstract' base class for QueryInput scripts. 
    """
    
    @classmethod
    def get_sets(cls, project):
        """
        Return the sets of the given project that are suitable as input for this script.
        By default, returns all fields in the project.
        """
        return project.all_articlesets()

    @classmethod
    def get_options_form(cls, project, sets, **options):
        """Return the form with filter values specified for this project/sets

        By default, returns:
        - the options_form with project and article set filled in and hidden
        - plus any filter fields returned by get_fields
        - plus a multichoice list of output fields from get_fields
        """

        p = project
        fields = cls.get_fields(project, sets)
        fieldnames = [(field.label, field.label) for field in fields]

        class Form(forms.Form):
            project = forms.ModelChoiceField(queryset=Project.objects.filter(pk=p.id), initial=p)
            project.widget = forms.HiddenInput()
            # how to specify initial value for multi choice?
            articlesets = forms.ModelMultipleChoiceField(queryset=ArticleSet.objects.filter(pk__in=sets), initial=" ".join(str(s) for s in sets))
            articlesets.widget = forms.HiddenInput()

            Fields = forms.MultipleChoiceField(choices=fieldnames)

            def clean_fields(self, cleanedData):
                raise Exception(cleanedData)
            

        for field in fields:
            if field.can_filter:
                for label, form_field in field.get_form_fields(project, sets):
                    # add to attribute and base_fields
                    setattr(Form, label, form_field)
                    Form.base_fields[label] = form_field


        return Form


###########################################################################
#                          U N I T   T E S T S                            #
###########################################################################

from amcat.tools import amcattest

class InputTestSetup(object):
    def setUp(self):
        self.p = amcattest.create_test_project()
        self.indexed_set, self.unindexed_set, self.coding_set = [amcattest.create_test_set(project=self.p, articles=5+i) for i in range(3)]
        self.all_sets = (self.indexed_set, self.unindexed_set, self.coding_set)
        for s in self.all_sets:
            s.indexed = s == self.indexed_set
            s.index_dirty = False
            s.save()
        self.job = amcattest.create_test_job(project=self.p, articleset=self.coding_set)
    
    
