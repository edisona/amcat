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

"""ORM Module representing projects"""

from __future__ import unicode_literals, print_function, absolute_import

from functools import partial

from django.contrib.auth.models import User, Permission
from django.utils.functional import SimpleLazyObject

from amcat.tools.model import AmcatModel
from amcat.tools.toolkit import wrapped

from amcat.models.coding.codebook import Codebook
from amcat.models.coding.codingschema import CodingSchema
from amcat.models.article import Article
from amcat.models.articleset import ArticleSetArticle, ArticleSet

from django.db import models
from django.db.models import Q

from django.contrib.contenttypes.models import ContentType

LITTER_PROJECT_ID = 1

def get_default_guest_role():
    """
    Returns the lowest possible defined permission (not null, which means the
    project is not readable for guests.
    """
    return Permission.objects.get(
        content_type=ContentType.objects.get_for_model(Project),
        codename=Project._meta.permissions[0][0]
    )

def get_project_permissions():
    return Permission.objects.filter(
        content_type=ContentType.objects.get_for_model(Project),
        codename__in=dict(Project._meta.permissions).keys()
    )

class Project(AmcatModel):
    """Model for table projects.

    Projects are the main organizing unit in AmCAT. Most other objects are
    contained within a project: articles, sets, codingjobs etc.

    Projects have users in different roles. For most authorisation questions,
    AmCAT uses the role of the user in the project that an object is contained in
    """
    __label__ = 'name'

    id = models.AutoField(primary_key=True, db_column='project_id', editable=False)

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, null=True)

    insert_date = models.DateTimeField(db_column='insertdate', auto_now_add=True)
    owner = models.ForeignKey(User, db_column='owner_id')

    insert_user = models.ForeignKey(User, db_column='insertuser_id',
                                    related_name='inserted_project',
                                    editable=False)

    guest_role = models.ForeignKey(Permission, null=True, default=get_default_guest_role)

    active = models.BooleanField(default=True)
    index_default = models.BooleanField(default=True)

    # Coding fields
    codingschemas = models.ManyToManyField("amcat.CodingSchema", related_name="projects_set")
    codebooks = models.ManyToManyField("amcat.Codebook", related_name="projects_set")
    articlesets = models.ManyToManyField("amcat.ArticleSet", related_name="projects_set")

    def get_codingschemas(self):
        """
        Return all codingschemas connected to this project. This returns codingschemas
        owned by it and linked to it.
        """
        return CodingSchema.objects.filter(Q(projects_set=self)|Q(project=self))

    def get_codebooks(self):
        """
        Return all codebooks connected to this project. This returns codebooks 
        owned by it and linked to it.
        """
        return Codebook.objects.filter(Q(projects_set=self)|Q(project=self))
    
    @property
    def users(self):
        """Get a list of all users with some role in this project"""
        return (r.user for r in self.projectrole_set.all())

    def all_articlesets(self):
        """
        Get a set of articlesets either owned by this project or
        contained in a set owned by this project
        """
        return ArticleSet.objects.filter(Q(project=self)|Q(projects_set=self)).distinct()

    def all_articles(self):
        """
        Get a set of articles either owned by this project
        or contained in a set owned by this project
        """
        return Article.objects.filter(Q(articlesets_set__project=self)|Q(project=self)).distinct()
            
    def get_all_article_ids(self):
        """
        Get a sequence of article ids either owned by this project
        or contained in a set owned by this project
        """
        for a in Article.objects.filter(project=self).only("id"):
            yield a.id
        for asa in ArticleSetArticle.objects.filter(articleset__project=self):
            yield asa.article_id
        
    class Meta():
        db_table = 'projects'
        app_label = 'amcat'
        ordering = ('name',)
        permissions = (
            # MUST be defined in ascending order: the nth permisson has the same
            # or more permissions than the (n-1)th permission.
            ("can_view_meta", "Can view meta information"),
            ("can_view", "Can view all information"),
            ("can_edit", "Can add/edit/delete codingjobs, codebooks, .."),
            ("can_manage", "Can edit members, description, ..")
        )

# Can be used to refer to permssions from outside this module.
PERMISSION_META, PERMISSION_VIEW, PERMISSION_EDIT, PERMISSION_MANAGE = (
    SimpleLazyObject(get_project_permissions().filter(codename=c).get for c in
        ("can_view_meta", "can_view", "can_edit", "can_manage")
    )
)

###########################################################################
#                          U N I T   T E S T S                            #
###########################################################################
        
from amcat.tools import amcattest

class TestProject(amcattest.PolicyTestCase):
    def test_create(self):
        """Can we create a project and access its attributes?"""
        p = amcattest.create_test_project(name="Test")
        self.assertEqual(p.name, "Test")

        
    def test_all_articles(self):
        """Does getting all articles work?"""
        from django.db.models.query import QuerySet

        p1, p2 = [amcattest.create_test_project() for _x in [1,2]]
        a1, a2 = [amcattest.create_test_article(project=p) for p in [p1, p2]]
        self.assertEqual(set(p1.get_all_article_ids()), set([a1.id]))
        self.assertEqual(set(p1.all_articles()), set([a1]))
        
        s = amcattest.create_test_set(project=p1)
        self.assertEqual(set(p1.get_all_article_ids()), set([a1.id]))
        self.assertEqual(set(p1.all_articles()), set([a1]))
        s.add(a2)
        self.assertEqual(set(p1.get_all_article_ids()), set([a1.id, a2.id]))
        self.assertEqual(set(p1.all_articles()), set([a1, a2]))
        self.assertTrue(isinstance(p1.all_articles(), QuerySet))

    def test_all_articlesets(self):
        """Does getting all articlesets work?"""
        from django.db.models.query import QuerySet

        p1, p2 = [amcattest.create_test_project() for _x in [1,2]]
        a1 = amcattest.create_test_set(5, project=p1)
        a2 = amcattest.create_test_set(5, project=p2)

        self.assertEqual(set([a1]), set(p1.all_articlesets()))
        p1.articlesets.add(a2)
        self.assertEqual({a1, a2}, set(p1.all_articlesets()))
        self.assertTrue(isinstance(p1.all_articlesets(), QuerySet))


