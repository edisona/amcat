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

from django.conf.urls.defaults import patterns, url

from navigator.views.project import project

# These patterns are prepended with (?P<project_id>[0-9]+)
project_patterns = patterns(
    '',
    # Articles
    url(r'^article/(?P<id>[0-9]+)$', project.article),
    url(r'^articleset/(?P<id>[0-9]+)$', project.articleset, name="articleset"),
    url(r'^articleset/edit/(?P<id>[0-9]+)$', project.edit_articleset, name="articleset-edit"),
    url(r'^articleset/delete/(?P<id>[0-9]+)$', project.delete_articleset, name="articleset-delete"),
    url(r'^articleset/unlink/(?P<id>[0-9]+)$', project.unlink_articleset, name="articleset-unlink"),
    url(r'^articleset/deduplicate/(?P<id>[0-9]+)$', project.deduplicate_articleset, name="articleset-deduplicate"),
    url(r'^articleset/importable$', project.show_importable_articlesets, name="articleset-importable"),
    url(r'^articleset/name-import/(?P<id>[0-9]+)$$', project.import_articleset, name="articleset-import"),

    # Overviews
    url(r'^$', project.view, name='project'),
    url(r'^articlesets$', project.articlesets, name='project-articlesets'),
    url(r'^selection$', project.selection, name='project-selection'),
    url(r'^codingjobs$', project.codingjobs, name='project-codingjobs'),
    url(r'^schemas$', project.schemas, name='project-schemas'),
    url(r'^codebooks$', project.codebooks, name='project-codebooks'),
    url(r'^users$', project.users, name='project-users'),
)

urlpatterns = patterns(
    '',
    # Project report
    url(r'^$', project.my_active, name='projects'),
    url(r'^my_all$', project.my_all),
    url(r'^all$', project.all),
    url(r'^add$', project.add, name='project-add'),

    # Include project-specific urls
    urls("^(?P<project_id>[0-9]+)/", include(project_patterns)),

    # Projects (+managers)


    url(r'^edit$', 'navigator.views.project.edit', name='project-edit'),
    url(r'^users/add$', 'navigator.views.project.users_add'),
    url(r'^upload-articles$', 'navigator.views.project.upload_article', name='upload-articles'),
    url(r'^upload-articles/scrapers$', 'navigator.views.project.scrape_articles', name='scrape-articles'),

    url(r'^upload-articles/(?P<plugin>[0-9]+)$', 'navigator.views.project.upload_article_action', name='upload-articles-action'), 
    url(r'^user/(?P<user>[0-9]+)$', 'navigator.views.project.project_role'),

    url(r'^codebook/(?P<codebook>[-0-9]+)$', 'navigator.views.project.codebook', name='project-codebook'),
    url(r'^codebook/(?P<codebook>[-0-9]+)/save_labels$', 'navigator.views.project.save_labels'),
    url(r'^codebook/(?P<codebook>[-0-9]+)/save_name$', 'navigator.views.project.save_name'),
    url(r'^codebook/(?P<codebook>[-0-9]+)/save_changesets$', 'navigator.views.project.save_changesets'),
    url(r'^codebook/add$', 'navigator.views.project.add_codebook', name='project-add-codebook'),
    url(r'^schema/(?P<schema>[-0-9]+)$', 'navigator.views.project.schema', name='project-schema'),
    url(r'^schema/new$', 'navigator.views.project.new_schema', name='project-new-schema'),
    url(r'^schema/(?P<schema>[-0-9]+)/edit$', 'navigator.views.project.edit_schema', name='project-edit-schema'),
    url(r'^schema/(?P<schema>[-0-9]+)/copy$', 'navigator.views.project.copy_schema', name='project-copy-schema'),
    url(r'^schema/(?P<schema>[-0-9]+)/name$', 'navigator.views.project.name_schema', name='project-name-schema'),
    url(r'^schema/(?P<schema>[-0-9]+)/edit/schemafield/(?P<schemafield>[0-9]+)$', 'navigator.views.project.edit_schemafield', name='project-edit-schemafield'),
    url(r'^schema/(?P<schema>[-0-9]+)/edit/schemafield/(?P<schemafield>[0-9]+)/delete$', 'navigator.views.project.delete_schemafield', name='project-delete-schemafield'),

    url(r'^add_codingjob$', 'navigator.views.project.add_codingjob', name='codingjob-add'),
    url(r'^codingjob/(?P<codingjob>[0-9]+)$', 'navigator.views.project.view_codingjob', name='codingjob'),
    url(r'^import$', 'navigator.views.project.import_codebooks', name='codebook-import'),
) 
