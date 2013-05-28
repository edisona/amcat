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

from django.forms import Textarea, ModelForm, HiddenInput

from django.core.urlresolvers import reverse
from django.views.generic.base import View, TemplateResponseMixin, ContextMixin, TemplateView
from django.views.generic.detail import SingleObjectMixin

from amcat.models import RuleSet, Rule
from django.forms.formsets import formset_factory
from django.forms.models import BaseModelFormSet

from api.rest.resources import ProjectResource as RuleSetResource
from navigator.views.datatableview import DatatableCreateView

class RuleForm(ModelForm):
    class Meta:
        model = Rule
        fields = ["id", "ruleset", "order", "label", "where", "insert", "delete", "remarks"]
        widgets = {field : Textarea(attrs={'cols': 5, 'rows': 4})
                   for field in ["insert","delete","where","remarks"]}
        widgets["ruleset"] = HiddenInput
    
class RuleSetTableView(DatatableCreateView):
    model = RuleSet
    rowlink_urlname = "ruleset"
    
class RuleSetView(View, TemplateResponseMixin, SingleObjectMixin):
    model = RuleSet
    template_name = "navigator/rule/ruleset.html"

    def get(self, request, pk, **kwargs):
        self.object = self.get_object()

        formset = formset_factory(RuleForm, formset=BaseModelFormSet, can_delete=True)
        formset.model = Rule
        formset = formset(queryset=self.object.rules.all())
        
        return self.render_to_response(self.get_context_data(formset=formset))
    
    def post(self, request, pk, **kwargs):
        self.object = self.get_object()
        ruleset_id = self.object.id
        class RuleFormWithRuleset(RuleForm):
            def clean(self):
                # HACK! How to add ruleset info to extra fields in a meaningful way?
                cleaned_data = super(RuleForm, self).clean()
                if "ruleset" not in cleaned_data and len(self._errors.get("ruleset", [])) == 1 and self._errors["ruleset"][0] == u"This field is required.":
                    cleaned_data["ruleset"] = RuleSet.objects.get(pk=ruleset_id)
                    del self._errors["ruleset"]
                return cleaned_data
        
        formset = formset_factory(RuleFormWithRuleset, formset=BaseModelFormSet, can_delete=True)
        formset.model = Rule
        formset = formset(request.POST, request.FILES, queryset=self.object.rules.all())
        if formset.is_valid():
            formset.save()
            formset = formset_factory(RuleForm, formset=BaseModelFormSet, can_delete=True)
            formset.model = Rule
            formset = formset(queryset=self.object.rules.all())


        return self.render_to_response(self.get_context_data(formset=formset))
