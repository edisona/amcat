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

from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.forms.models import modelform_factory

from api.rest.datatable import Datatable
from api.rest.resources import ArticleSetResource, ArticleMetaResource

from amcat.models import Project, ArticleSet

from api.rest.count import count

"""
"""

__all__ = ("ProjectArticlesets", "ArticlesetView")

class ProjectArticlesets(AuthViewMixin, MenuViewMixin, TemplateView):
    template_name = "navigator/project/articlesets/overview.html"
    check_instances = (Project,)

    @property
    def articlesets(self):
        return Datatable(ArticleSetResource, rowlink="./articlesets/{id}").hide("project")

    def get_context_data(self, **kwargs):
        project = self.object_map["project"]

        ctx = super(ProjectArticlesets, self).get_context_data(**kwargs)
        ctx.update({
            "owned_articlesets" : self.articlesets.filter(project=project, codingjob_set__id='null'),
            "imported_articlesets" : self.articlesets.filter(projects_set=project)
        })

        return ctx

class UploadArticles(AuthViewMixin, MenuViewMixin, TemplateView):
    """View for choosing which scraper a user wants to use to upload articles"""
    privileges = ("")
    pass

class ScrapeArticles(AuthViewMixin, MenuViewMixin, TemplateView):
    pass

class ArticlesetView(AuthViewMixin, MenuViewMixin, TemplateView):
    template_name = "navigator/project/articlesets/view.html"
    check_instances = (Project, ArticleSet)

    @property
    def articleset(self):
        return self.object_map["articleset"]

    @property
    def articles(self):
        return (Datatable(ArticleMetaResource, rowlink="./{}/{{id}}".format(self.articleset.id))
                    .filter(articlesets_set=self.articleset).hide("uuid", "project"))

    def get_context_data(self, **kwargs):
        ctx = super(ArticlesetView, self).get_context_data(**kwargs)
        ctx.update({
            "articles":self.articles,
            "articlecount":count(self.articleset.articles.all())
        })
        return ctx
    
