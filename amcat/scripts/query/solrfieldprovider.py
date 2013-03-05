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
Input script that uses the solr full text index to filter and/or annotate articles
"""

from __future__ import unicode_literals, print_function, absolute_import
from amcat.scripts.query import field
from django import forms
from amcat.tools.amcatsolr import Solr, filters_from_form
from amcat.models import ArticleSet
from amcat.tools.table import table3
from amcat.scripts.query.fieldprovider import FieldProvider

# todo fix the mess with classmethods and instances
# (ie make some sane policy on what gets instantiated when)

class SolrColumn(table3.ObjectColumn):
    """Object Column that uses a 'hits' dict to provide the #hits for a specific query+article"""
    def __init__(self, label, hits, table):
        """
        @param hits: a dictionary of article id to #hits
        """
        super(SolrColumn, self).__init__(label)
        self.hits = hits
        self.table = table
    def getCell(self, row):
        return self.hits.get(self.table.get_column_value(row, "id"), 0)

class SolrFieldProvider(FieldProvider):
    """FieldProvider based on article meta data"""
    label = "Search terms"
    clean_label = "solr_queries"

    @classmethod
    def get_filter_fields(cls, sets):
        """Only provide fields if all sets are 'fully indexed'"""
        sets = ArticleSet.objects.filter(pk__in=sets).only("indexed", "index_dirty")
        if all(s.indexed and not s.index_dirty for s in sets):
            yield cls.label, forms.CharField(required=False, widget=forms.Textarea)

    @classmethod
    def get_output_fields(cls, sets):
        sets = ArticleSet.objects.filter(pk__in=sets).only("indexed", "index_dirty")
        if all(s.indexed and not s.index_dirty for s in sets):
            yield cls.label

    @classmethod
    def clean_form(cls, cleaned_data):
        # todo insert old code with hashtags etc here
        queries = cleaned_data.get(cls.label, "").strip()
        if queries:
            cleaned_data[cls.clean_label] = queries.split("\n")
        elif cls.label in cleaned_data["Columns"]: 
            raise forms.ValidationError("Selected {cls.label} column without specifying any search terms"
                                        .format(**locals()))
            
    def filter(self, table):
        """If there are queries, filter out articles that match none of the queries"""
        # possible optimization: query and remember scores if field is selceted as column
        # possible optimization: filter on medium etc from cleaned_data as well
        # possible change: make use as filter optional
        queries = self.cleaned_data.get(self.clean_label)
        if queries:
            query = " OR ".join("({})".format(query) for query in queries)
            filters = [" OR ".join('sets:%d' % s.id for s in self.cleaned_data['articlesets'])]
            ids = [row["id"] for row in Solr().query_all(query, filters=filters, fields=["id"], score=False)]
            
            table.queryset = table.queryset.filter(pk__in=ids)

    def add_columns(self, table):
        if self.label in self.output_fields:
            queries = self.cleaned_data[self.clean_label]
            filters = [" OR ".join('sets:%d' % s.id for s in self.cleaned_data['articlesets'])]
            hits = {} # {query, id : score}}
            for query in queries:
                hits = {}
                for row in Solr().query_all(query, filters=filters, fields=["id"]):
                    hits[row["id"]] = row["score"]
                table.addColumn(SolrColumn(query, hits, table))
