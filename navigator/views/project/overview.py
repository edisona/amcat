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

from navigator.menu import MenuViewMixin
from navigator.utils.auth import AuthViewMixin
from navigator.utils.misc import session_pop
from navigator.forms import ProjectForm

from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic.edit import FormView, CreateView
from django.views.generic.base import TemplateView
from django.forms.models import modelform_factory
from django.shortcuts import redirect

from amcat.models.authorisation import ProjectPermission, get_project_permissions
from amcat.models import Project#, ProjectRole, Role

import logging; log = logging.getLogger(__name__)

"""
This module contains all pages with links to projects (my projects,
all projects, active projects..)
"""

__all__ = ("ProjectOverview", "ProjectEdit", "ProjectAdd")

PROJECT_EDIT = "project_{project.id}_edited"
PROJECT_NEW = "project_{project.id}_new"

ProjectForm = modelform_factory(Project, form=ProjectForm, fields=
    ("name", "description", "guest_role", "active", "index_default")
)

class ProjectOverview(AuthViewMixin, MenuViewMixin, TemplateView):
    template_name = "navigator/project/overview/view.html"
    check_instances = (Project,)

    def get_context_data(self, **kwargs):
        edit_key = PROJECT_EDIT.format(**self.object_map)
        new_key = PROJECT_NEW.format(**self.object_map)

        ctx = super(ProjectOverview, self).get_context_data(**kwargs)
        ctx.update({
            "edited" : session_pop(self.request.session, edit_key),
            "new" : session_pop(self.request.session, new_key),
        })

        return ctx

class ProjectEdit(AuthViewMixin, MenuViewMixin, FormView):
    template_name = "navigator/project/overview/edit.html"
    form_class = ProjectForm
    check_instances = (Project,)

    def form_valid(self, form):
        form.save()
        self.request.session[PROJECT_EDIT.format(**self.object_map)] = True
        return super(ProjectEdit, self).form_valid(form)

    def get_success_url(self):
        return reverse("project-overview", kwargs={"project_id":self.object_map["project"].id})

    def get_form_kwargs(self, **kwargs):
        kws = super(ProjectEdit, self).get_form_kwargs(**kwargs)
        kws.update(dict(instance=self.object_map["project"]))
        return kws

class ProjectAdd(AuthViewMixin, MenuViewMixin, CreateView):
    template_name = "navigator/project/add.html"
    form_class = ProjectForm
    check_models = (Project,)

    def form_valid(self, form):
        # Save form with additional info
        p = form.save(commit=False)
        p.owner = p.insert_user = self.request.user
        p.save()

        # Set a role as admin
        pr = ProjectPermission(
            permission=get_project_permissions().order_by("-id")[0],
            project=p, user=self.request.user
        )
        pr.save()

        # Set session variable to indicate the just made project is new
        self.request.session[PROJECT_NEW.format(project=p)] = True

        # Redirect to success url. This is what our parent would do, but it
        # doesn't accept a commit=False, so we have to do it ourselves.
        self.object = p
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse("project", kwargs=dict(project_id=self.object.id))

    def dispatch(self, *args, **kwargs):
        res = super(ProjectAdd, self).dispatch(*args, **kwargs)
        return res

    def get_context_data(self, **kwargs):
        ctx = super(ProjectAdd, self).get_context_data(**kwargs)
        ctx.update({"cancel":reverse("projects")})
        return ctx

