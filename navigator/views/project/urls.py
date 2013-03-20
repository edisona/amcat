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
This is the urlrouter for everything within a project. Each specific object
(articlesets, articles, schemas, etc.) gets its own patterns, which is included
by the main patterns.
"""

from django.core.urlresolvers import reverse_lazy
from django.conf.urls.defaults import patterns, url, include
from django.views.generic.simple import redirect_to

from navigator.views.project import project
from navigator.views import project as projectn

# Router for article-pages
article_patterns = patterns('',
    url(r'^$', project.article, name="articleset-article")
)

# Router for articleset-pages
articleset_patterns = patterns('',
    url(r'^$', project.articleset, name="articleset"),
    url(r'^edit$', project.edit_articleset, name="articleset-edit"),
    url(r'^delete$', project.delete_articleset, name="articleset-delete"),
    url(r'^unlink$', project.unlink_articleset, name="articleset-unlink"),
    url(r'^deduplicate$', project.deduplicate_articleset, name="articleset-deduplicate"),
    url(r'^name-import$', project.import_articleset, name="articleset-import"),

    # Articles
    url(r'^article/(?P<article_id>[0-9]+)/$', include(article_patterns))
)

# Router for user-pages
user_patterns = patterns('',
    url(r'^$', project.project_role),
)

# Router for codebook-pages
codebook_patterns = patterns('',
    url(r'^$', project.codebook, name='project-codebook'),
    url(r'^add$', project.add_codebook, name='project-add-codebook'),
    url(r'^save_labels$', project.save_labels),
    url(r'^save_name$', project.save_name),
    url(r'^save_changesets$', project.save_changesets),
)

codingschemafield_patterns = patterns('',
    url(r'^$', project.edit_schemafield, name='project-edit-schemafield'),
    url(r'^delete$', project.delete_schemafield, name='project-delete-schemafield'),
)

codingschema_patterns = patterns('',
    url(r'^$', project.schema, name='project-schema'),
    url(r'^edit$', project.edit_schema, name='project-edit-schema'),
    url(r'^copy$', project.copy_schema, name='project-copy-schema'),
    url(r'^name$', project.name_schema, name='project-name-schema'),
    url(r'^field/(?P<codingschemafield_id>[0-9]+)', include(codingschemafield_patterns))
)

codingjob_patterns = patterns('',
    url(r'^$', project.view_codingjob, name='project-codingjob'),
)

# For everything within a specific project
project_patterns = patterns('',
    # Delegating to more specific routers
    url(r'^user/(?P<user_id>[0-9]+)/', include(user_patterns)),
    url(r'^articleset/(?P<artcleset_id>[0-9]+)/', include(articleset_patterns)),
    url(r'^codebook/(?P<codebook_id>[0-9]+)/', include(codebook_patterns)),
    url(r'^codingschema/(?P<codingschema_id>[0-9]+)/', include(codingschema_patterns)),
    url(r'^codingjob/(?P<codingjob_id>[0-9]+)/', include(codingjob_patterns)),

    # Articlesets
    url(r'^importable$', project.show_importable_articlesets, name="articleset-importable"),

    # Overviews
    url(r'^$', redirect_to, {"url":"./overview"}, name='project'),
    url(r'^overview$', projectn.ProjectOverview.as_view(), name='project-overview'),
    url(r'^articlesets$', project.articlesets, name='project-articlesets'),
    url(r'^selection$', project.selection, name='project-selection'),
    url(r'^codingjobs$', project.codingjobs, name='project-codingjobs'),
    url(r'^schemas$', project.schemas, name='project-schemas'),
    url(r'^codebooks$', project.codebooks, name='project-codebooks'),
    url(r'^users$', project.users_view, name='project-users'),

    # Actions
    url(r'^edit$', projectn.ProjectEdit.as_view(), name='project-edit'),
    url(r'^add-user$', project.users_add, name='project-user-add'),
    url(r'^add-codingschema$', project.new_schema, name='project-add-schema'),
    url(r'^add-codingjob$', project.add_codingjob, name='project-add-codingjob'),
    url(r'^upload-articles$', project.upload_article, name='project-upload-articles'),
    url(r'^upload-articles/scrapers$', project.scrape_articles, name='project-scrape-articles'),
    url(r'^upload-articles/plugin/(?P<plugin>[0-9]+)$', project.upload_article_action, name='project-upload-articles-action'), 
    url(r'^import$', project.import_codebooks, name='project-codebook-import'),
)

# Main router
urlpatterns = patterns('',
    # Project report
    url(r'^$', redirect_to, {"url":reverse_lazy("my-active-projects")}, name='projects'),
    url(r'^my_active$', projectn.MyActiveProjects.as_view(), name="my-active-projects"),
    url(r'^my_all$', projectn.MyProjects.as_view(), name="all-my-projects"),
    url(r'^all$', projectn.AllProjects.as_view(), name="all-projects"),
    url(r'^add$', project.add, name='project-add'),

    # Include project-specific urls
    url("^(?P<project_id>[0-9]+)/", include(project_patterns)),
) 
