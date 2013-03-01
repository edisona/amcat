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
Explicit representation of the fields (columns) yielded by input sources.
Some fields can be used for filtering on (e.g. date, medium) while others
can only be used as output (text). Fields can also specify specific filter
representations (e.g. between/from/before for dates). Some fields, e.g. the
coded values, are created dynamically based on selected project/sets
"""
from django import forms
from django.db.models import fields

from amcat.scripts.forms import ModelMultipleChoiceFieldWithIdLabel
from amcat.models import Article

class QueryField(object):
    """
    Base class for query fields
    """
    def __init__(self, label, can_filter=False):
        self.label = label
        self.can_filter = can_filter

class FilterField(QueryField):
    """
    Field that can be used for filtering
    """
    def __init__(self, label, can_filter=True):
        return super(FilterField, self).__init__(label, can_filter)
    
    def get_form_fields(self, project, sets):
        """Return the form fields needed to filter on this field"""
        raise NotImplemented()
    def clean_fields(self, cleanedData):
        """Optional post processing of the fields"""
        return cleanedData

    
class ArticleField(FilterField):
    """
    Filter field based on an article property (e.g. date, medium, section)
    The given label.lower() should be in Article._meta.fields.
    """

    def get_form_fields(self, project, sets):
        field = Article._meta.get_field_by_name(self.label.lower())[0]
        return FIELD_MAP[field.__class__](field, sets)

def get_nominal_form_fields(field, sets):
    """Get the form_fields assuming that the property is a nominal primitive (e.g. enumerable)"""
    


class ArticleField(FilterField):
    def __init__(self, label, can_filter, field):
        super(ArticleField, self).__init__(label, can_filter)
        self.field = field

class ArticleChoiceField(ArticleField):
    django_field = (fields.TextField, fields.CharField)

    def get_choices(self, sets):
        yield ('--- all ---', '--- all ---')
        articles = Article.objects.filter(articlesets_set__in=sets)
        for choice, in sorted(set(articles.values_list(self.field.name.lower()))):
            if choice is None:
                choice = '--- empty ---'
            yield (choice, choice)

    def get_form_fields(self, project, sets):
        yield self.label, forms.MultipleChoiceField(choices=list(self.get_choices(sets)), required=False)
        
class ArticleForeignKeyField(ArticleField):
    """Foreign Key fields on articles, assumes that parent_model.objects.filter(article__*) works"""
    django_field = fields.related.ForeignKey
    def get_form_fields(self, project, sets):
        qs = self.field.related.parent_model.objects.filter(article__articlesets_set__in=sets).distinct()
        yield self.field.name, ModelMultipleChoiceFieldWithIdLabel(queryset=qs, required=False)
        
class ArticleDateRangeField(ArticleField):
    django_field = fields.DateTimeField
    DATETYPES = {
        "all" : "All Dates",
        "on" : "On",
        "before" : "Before",
        "after" : "After",
        "between" : "Between",
        }

    def get_form_fields(self, project, sets):
        yield "{self.label}_type".format(**locals()), forms.ChoiceField(choices=self.DATETYPES.items(), initial='all')
        for suffix in ('start', 'end', 'on'):
            yield "{self.label}_{suffix}".format(**locals()), forms.DateField(input_formats=('%d-%m-%Y',), required=False)

def article_field(label, can_filter=True):
    """
    Return the right article field based on the type of field
    @param field: the name of a field in Article._meta.fields
    """
    field = Article._meta.get_field_by_name(label.lower())[0]

    for cls in (ArticleChoiceField, ArticleForeignKeyField, ArticleDateRangeField):
        print("Checking isintance({field}, {cls.django_field})={x}".format(x=isinstance(field, cls.django_field), **locals()))
        if isinstance(field, cls.django_field):
            return cls(label, can_filter, field)
    raise ValueError("Cannot handle article field {label} of type {field.__class__.__name__}".format(**locals()))


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
    
                
    
