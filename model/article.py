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
Model module containing the Article class representing documents in the
articles database table
"""

from __future__ import unicode_literals, print_function, absolute_import

from amcat.tools.model import AmcatModel

from amcat.model.project import Project
from amcat.model.medium import Medium
from amcat.model.sentence import Sentence

from amcat.tools import toolkit

from django.db import models

import logging; log = logging.getLogger(__name__)

#class ArticleSentences(AmcatModel):
#    article = 

  
class Article(AmcatModel):
    """
    Class representing a newspaper article
    """
    id = models.IntegerField(primary_key=True, db_column="article_id")

    date = models.DateTimeField()
    section = models.CharField(null=True, max_length=80)
    pagenr = models.IntegerField(null=True)
    headline = models.CharField(max_length=200)
    byline = models.TextField(null=True, max_length=200)
    length = models.IntegerField()
    metastring = models.TextField(null=True)
    url = models.URLField(null=True)
    externalid = models.IntegerField(null=True)

    sets = models.ManyToManyField("models.Set", db_table="sets_articles")
    
    text = models.TextField()

    project = models.ForeignKey(Project)
    medium = models.ForeignKey(Medium)

    def __unicode__(self):
        return self.headline

    class Meta():
        db_table = 'articles'
        app_label = 'models'

    def words(self):
        "@return: a generator yielding all words in all sentences"
        for sentence in self.sentences:
            for word in sentence.words:
                yield word

    def getSentence(self, parnr, sentnr):
        "@return: a Sentence object with the given paragraph and sentence number"
        for s in self.sentences:
            if s.parnr == parnr and s.sentnr == sentnr:
                return s

    ## Auth ##
    def can_read(self, user):
        if self.project in user.projects: return True
        if user.roles.filter(label='admin'): return True

        if user.projectrole_set.filter(project__sets__article=self):
            return True
        return False


class ArticlePosting(AmcatModel):
    """Proxy for Article.children and Article.parent"""
    article = models.ForeignKey(Article, db_column='article_id')
    parent = models.ForeignKey(Article, db_column='parent_article_id', related_name='articleposting_parent')

    class Meta():
        db_table = 'articles_postings'
        app_label = 'models'