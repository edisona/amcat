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
Input script that yields 'meta' data about articles, including headline and text
"""

from __future__ import unicode_literals, print_function, absolute_import
from amcat.scripts.query.fieldprovider import FieldProvider
from django import forms
from django.db.models import fields

from amcat.scripts.forms import ModelMultipleChoiceFieldWithIdLabel
from amcat.models import Article

from amcat.tools.table import table3 

class QuerySetColumn(table3.ObjectColumn):

    def __init__(self, label, column_name, table):
        super(QuerySetColumn, self).__init__(label)
        self.column_name = column_name
        self.table = table
    def getCell(self, row):
        return self.table.get_column_value(row, self.column_name)

class ArticleMetaFieldProvider(FieldProvider):
    """FieldProvider based on article meta data"""

    @classmethod
    def get_field(cls, label, can_filter=True):
        """
        Return the right article field based on the type of field
        @param field: the name of a field in Article._meta.fields
        """
        field = Article._meta.get_field_by_name(label.lower())[0]
        for cls in (ArticleChoiceField, ArticleForeignKeyField, ArticleDateRangeField):
            if isinstance(field, cls.django_field):
                return cls(label, can_filter, field)
        raise ValueError("Cannot handle article field {label} of type {field.__class__.__name__}".format(**locals()))
    
    @classmethod
    def get_fields(cls):
        return [cls.get_field(f) for f in ['Medium', 'Author', 'Section', 'Date']]
    
    @classmethod
    def get_filter_fields(cls, sets):
        for field in cls.get_fields():
            if field.can_filter:
                for label, form_field in field.get_form_fields(sets):
                    yield label, form_field

    @classmethod
    def get_output_fields(cls, sets):
        return (field.label for field in cls.get_fields())
                    
    def __init__(self, *args, **kargs):
        super(ArticleMetaFieldProvider, self).__init__(*args, **kargs)
        self.fields = self.get_fields()

    def filter(self, table):
        for field in self.fields:
            if field.can_filter:
                table.queryset = field.filter(table.queryset, self.cleaned_data)
            if field.label in self.output_fields:
                table.selected_columns.add(field.field.name)
                
    def add_columns(self, table):
        for field in self.fields:
            if field.label in self.output_fields:
                table.addColumn(QuerySetColumn(field.label, field.field.name, table))

class ArticleField(object):
    """Auxilliary class that represents a single 'meta' field of an article (eg healdine, data)"""
    
    def __init__(self, label, can_filter, field):
        """
        @param label: the label and form key for this field
        @param can_filter: does this field support filtering?
        @param field: the name of the article.xxx property represented by this ArticleField 
        """
        self.label = label
        self.can_filter = can_filter
        self.field = field
        
    def filter(self, results, cleaned_data):
        """
        Filter the results on the value of this field, if needed.
        Default behaviour calls _get_qs_filter if the cleaned_data includes
        and entry matching self.label
        @param results: a queryset representing the results so far
        @param form_values: the cleaned_data of the bound filter form
        """
        filter_data = self._get_filter_data(cleaned_data)
        if filter_data:
            filters = dict(self._get_qs_filters(filter_data))
            if filters:
                results = results.filter(**filters)
        return results

    def _get_filter_data(self, cleaned_data):
        """
        Return the relevant data to use for filtering, if any. 
        If None is returned, this field should not do any filtering
        """
        return cleaned_data.get(self.label)

    def _get_qs_filter(self, filter_data):
        """
        Return a mapping sequence to be used for filtering the articles queryset
        @return: a mapping sequence comprising valid keyword arguments to queryset.filter, or a False value to skip filtering
        """
        yield self.field.name, filter_data
        
class ArticleChoiceField(ArticleField):
    django_field = (fields.TextField, fields.CharField)

    def get_choices(self, sets):
        yield ('--- all ---', '--- all ---')
        articles = Article.objects.filter(articlesets_set__in=sets)
        for choice, in sorted(set(articles.values_list(self.field.name.lower()))):
            if choice is None:
                choice = '--- empty ---'
            yield (choice, choice)

    def get_form_fields(self, sets):
        yield self.label, forms.MultipleChoiceField(choices=list(self.get_choices(sets)), required=False)
        
    def _get_qs_filters(self, value):
        yield "{self.field.name}__in".format(**locals()), value
        
class ArticleForeignKeyField(ArticleField):
    """Foreign Key fields on articles, assumes that parent_model.objects.filter(article__*) works"""
    django_field = fields.related.ForeignKey
    def get_form_fields(self, sets):
        qs = self.field.related.parent_model.objects.filter(article__articlesets_set__in=sets).distinct()
        yield self.label, ModelMultipleChoiceFieldWithIdLabel(queryset=qs, required=False)
    def _get_qs_filters(self, value):
        yield "{self.field.name}__in".format(**locals()), value

class ArticleDateRangeField(ArticleField):
    django_field = fields.DateTimeField
    DATETYPES = {
        "all" : "All Dates",
        "on" : "On",
        "before" : "Before",
        "after" : "After",
        "between" : "Between",
        }

    def get_form_fields(self, sets):
        yield "{self.label}_type".format(**locals()), forms.ChoiceField(choices=self.DATETYPES.items(), initial='all', required=False)
        for suffix in ('start', 'end', 'on'):
            yield "{self.label}_{suffix}".format(**locals()), forms.DateField(input_formats=('%d-%m-%Y',), required=False)


    # def clean_fields(self, cleanedData):
    #     #TODO: Copy/paste from old forms.selectionform code, does not work yet!
    #     if cleanedData.get('datetype') in ('after', 'all') and 'endDate' in cleanedData:
    #         del cleanedData['endDate']
    #     if cleanedData.get('datetype') in ('before', 'all') and 'startDate' in cleanedData:
    #         del cleanedData['startDate']
    #     if cleanedData.get('datetype') == 'on':
    #         cleanedData['datetype'] = 'between'
    #         cleanedData['startDate'] = cleanedData['onDate'] 
    #         cleanedData['endDate'] = cleanedData['onDate'] + datetime.timedelta(1)
    #     missingDateMsg = "Missing date"
    #     if 'endDate' in cleanedData and cleanedData['endDate'] == None: 
    #         self._errors["endDate"] = self.error_class([missingDateMsg])
    #         del cleanedData['endDate']
    #     if 'startDate' in cleanedData and cleanedData['startDate'] == None: 
    #         self._errors["startDate"] = self.error_class([missingDateMsg])
    #         del cleanedData['startDate']
    #     #todo: shouldn't we validate enddate > startdate etc?
    #     return cleanedDaat
    
                
    

    
###########################################################################
#                          U N I T   T E S T S                            #
###########################################################################

from amcat.tools import amcattest
