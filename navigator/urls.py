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
from django.contrib.auth.views import password_change, password_change_done

urlpatterns = patterns(
    '',
     url(r'^$', 'navigator.views.report.index', name="index"),

    # Project report
    url(r'^projects$', 'navigator.views.project.my_active', name='projects'),
    url(r'^projects/my_all$', 'navigator.views.project.my_all'),
    url(r'^projects/all$', 'navigator.views.project.all'),

    # User report
    url(r'^users$', 'navigator.views.user.my_affiliated_active', name='users'),
    url(r'^users/my_all$', 'navigator.views.user.my_affiliated_all'),
    url(r'^users/all$', 'navigator.views.user.all', name='all-users'),

    url(r'^media$', 'navigator.views.report.media', name='media'),
    url(r'^nyi$', 'navigator.views.nyi.index', name='nyi'),
    
    url(r'^selection$', 'navigator.views.selection.index', name='selection'),

    # Articles
    url(r'^article/(?P<id>[0-9]+)$', 'navigator.views.article.view', name='article'),
    url(r'^project/(?P<projectid>[0-9]+)/article/(?P<id>[0-9]+)$', 'navigator.views.project.article'),
    url(r'^project/(?P<projectid>[0-9]+)/articleset/(?P<id>[0-9]+)$',
        'navigator.views.project.articleset', name="articleset"),
    url(r'^project/(?P<projectid>[0-9]+)/articleset/edit/(?P<id>[0-9]+)$',
        'navigator.views.project.edit_articleset', name="articleset-edit"),
    url(r'^project/(?P<projectid>[0-9]+)/articleset/delete/(?P<id>[0-9]+)$',
        'navigator.views.project.delete_articleset', name="articleset-delete"),
    url(r'^project/(?P<projectid>[0-9]+)/articleset/unlink/(?P<id>[0-9]+)$',
        'navigator.views.project.unlink_articleset', name="articleset-unlink"),
    url(r'^project/(?P<projectid>[0-9]+)/articleset/deduplicate/(?P<id>[0-9]+)$',
        'navigator.views.project.deduplicate_articleset', name="articleset-deduplicate"),
    url(r'^project/(?P<projectid>[0-9]+)/articleset/importable$',
        'navigator.views.project.show_importable_articlesets', name="articleset-importable"),
    url(r'^project/(?P<projectid>[0-9]+)/articleset/name-import/(?P<id>[0-9]+)$$',
        'navigator.views.project.import_articleset', name="articleset-import"),

    # Media
    url(r'^medium/add$', 'navigator.views.medium.add', name='medium-add'),

    # Users
    url(r'^user/(?P<id>[0-9]+)?$', 'navigator.views.user.view', name='user'),
    url(r'^user/edit/(?P<id>[0-9]+)$', 'navigator.views.user.edit', name='user-edit'),
    url(r'^user/add$', 'navigator.views.user.add', name='user-add'),
    url(r'^user/add-submit$', 'navigator.views.user.add_submit', name='user-add-submit'),
    url(r'^user/change-password$', password_change, name='user-change-password',
        kwargs=dict(
            template_name="navigator/user/change_password.html",
            post_change_redirect='change-password-done'
        )),
    url(r'^user/change-password-done$', password_change_done,
        kwargs=dict(
            template_name="navigator/user/change_password_done.html"
        )),


    # Plugins
    url(r'^plugins$', 'navigator.views.plugin.index', name='plugins'),
    url(r'^plugins/(?P<id>[0-9]+)$', 'navigator.views.plugin.manage', name='manage-plugins'),
    url(r'^plugins/(?P<id>[0-9]+)/add$', 'navigator.views.plugin.add', name='add-plugin'),
    
    # Projects (+managers)
    url(r'^project/add$', 'navigator.views.project.add', name='project-add'),
    url(r'^project/(?P<id>[0-9]+)$', 'navigator.views.project.view', name='project'),
    url(r'^project/(?P<id>[0-9]+)/articlesets$', 'navigator.views.project.articlesets', name='project-articlesets'),
    url(r'^project/(?P<id>[0-9]+)/selection$', 'navigator.views.project.selection', name='project-selection'),
    url(r'^project/(?P<id>[0-9]+)/codingjobs$', 'navigator.views.project.codingjobs', name='project-codingjobs'),
    url(r'^project/(?P<id>[0-9]+)/schemas$', 'navigator.views.project.schemas', name='project-schemas'),
    url(r'^project/(?P<id>[0-9]+)/codebooks$', 'navigator.views.project.codebooks', name='project-codebooks'),


    url(r'^project/(?P<id>[0-9]+)/edit$', 'navigator.views.project.edit', name='project-edit'),
    url(r'^project/(?P<id>[0-9]+)/users$', 'navigator.views.project.users_view', name='project-users'),
    url(r'^project/(?P<id>[0-9]+)/users/add$', 'navigator.views.project.users_add'),
    url(r'^project/(?P<id>[0-9]+)/upload-articles$', 'navigator.views.project.upload_article', name='upload-articles'),
    url(r'^project/(?P<id>[0-9]+)/upload-articles/scrapers$', 'navigator.views.project.scrape_articles', name='scrape-articles'),

    url(r'^project/(?P<project>[0-9]+)/upload-articles/(?P<plugin>[0-9]+)$', 'navigator.views.project.upload_article_action', name='upload-articles-action'), 
    url(r'^project/(?P<project>[0-9]+)/user/(?P<user>[0-9]+)$', 'navigator.views.project.project_role'),

    url(r'^project/(?P<project>[0-9]+)/codebook/(?P<codebook>[-0-9]+)$', 'navigator.views.project.codebook', name='project-codebook'),
    url(r'^project/(?P<project>[0-9]+)/codebook/(?P<codebook>[-0-9]+)/save_labels$', 'navigator.views.project.save_labels'),
    url(r'^project/(?P<project>[0-9]+)/codebook/(?P<codebook>[-0-9]+)/save_name$', 'navigator.views.project.save_name'),
    url(r'^project/(?P<project>[0-9]+)/codebook/(?P<codebook>[-0-9]+)/save_changesets$', 'navigator.views.project.save_changesets'),
    url(r'^project/(?P<id>[0-9]+)/codebook/add$', 'navigator.views.project.add_codebook', name='project-add-codebook'),
    url(r'^project/(?P<project>[0-9]+)/schema/(?P<schema>[-0-9]+)$', 'navigator.views.project.schema', name='project-schema'),
    url(r'^project/(?P<project>[0-9]+)/schema/new$', 'navigator.views.project.new_schema', name='project-new-schema'),
    url(r'^project/(?P<project>[0-9]+)/schema/(?P<schema>[-0-9]+)/edit$', 'navigator.views.project.edit_schema', name='project-edit-schema'),
    url(r'^project/(?P<project>[0-9]+)/schema/(?P<schema>[-0-9]+)/copy$', 'navigator.views.project.copy_schema', name='project-copy-schema'),
    url(r'^project/(?P<project>[0-9]+)/schema/(?P<schema>[-0-9]+)/name$', 'navigator.views.project.name_schema', name='project-name-schema'),
    url(r'^project/(?P<project>[0-9]+)/schema/(?P<schema>[-0-9]+)/edit/schemafield/(?P<schemafield>[0-9]+)$', 'navigator.views.project.edit_schemafield', name='project-edit-schemafield'),
    url(r'^project/(?P<project>[0-9]+)/schema/(?P<schema>[-0-9]+)/edit/schemafield/(?P<schemafield>[0-9]+)/delete$', 'navigator.views.project.delete_schemafield', name='project-delete-schemafield'),

    # Coding
    url(r'^coding/schema-editor$', 'navigator.views.schemas.index'),
    url(r'^coding/codingschema/(?P<id>[0-9]+)$', 'navigator.views.schemas.schema',
        name='codingschema'),


    #url(r'^codingjobs/(?P<coder_id>\d+|all)/(?P<status>all|unfinished)/$' ,'navigator.views.codingjob.index', name='codingjobs'),
    #url(r'^codingjobs$' ,'navigator.views.codingjob.index', name='codingjobs'),
    url(r'^codingjobs/(?P<coder_id>\d+)?$' ,'navigator.views.codingjob.index', name='codingjobs'),
    url(r'^codingjobs/(?P<coder_id>\d+)/all$' ,'navigator.views.codingjob.all', name='codingjobs-all'),
    url(r'^project/(?P<id>[0-9-]+)/add_codingjob$', 'navigator.views.project.add_codingjob', name='codingjob-add'),
    url(r'^project/(?P<project>[0-9-]+)/codingjob/(?P<codingjob>[0-9]+)$', 'navigator.views.project.view_codingjob', name='codingjob'),
    url(r'^project/(?P<id>[0-9-]+)/import$', 'navigator.views.project.import_codebooks', name='codebook-import'),
    url(r'^project/(?P<project>[0-9]+)/codingjob/(?P<codingjob>[0-9]+)/export-unit$', 'navigator.views.project.codingjob_unit_export', name='project-codingjob-unit-export'),
    url(r'^project/(?P<project>[0-9]+)/codingjob/(?P<codingjob>[0-9]+)/export-article$', 'navigator.views.project.codingjob_article_export', name='project-codingjob-article-export'),

    # Preprocessing
    url(r'^analysis/(?P<id>[0-9-]+)$', 'navigator.views.analysis.demo', name='analysis-demo'),
    url(r'^analysissentence/(?P<id>[0-9]+)$', 'navigator.views.analysis.sentence', name='analysis-sentence'),
    
    # Scrapers
    url(r'^scrapers$', 'navigator.views.scrapers.index', name='scrapers'),


    url(r'^semanticroles$', 'navigator.views.semanticroles.index', name='semanticroles'),
    url(r'^semanticroles/(?P<id>[0-9]+)$', 'navigator.views.semanticroles.sentence', name='semanticroles-sentence'),

) 