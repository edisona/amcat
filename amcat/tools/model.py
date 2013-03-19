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
from django.core.cache  import cache

from django.db import models
from django.core.exceptions import ValidationError
from amcat.tools.caching import _get_cache_key
from django_extensions.db.fields import UUIDField

__all__ = ['AmcatModel']

class AmcatModel(models.Model):
    """Replacement for standard Django-model, extending it with
    amcat-specific features."""
    __label__ = 'label'

    ### Check functions ###
    def can_read(self, user):
        return True

    def can_update(self, user):
        return self.can_read(user)

    def can_delete(self, user):
        return self.can_update(user)

    @classmethod
    def can_create(cls, user):
        return True

    class Meta():
        abstract=True
        app_label = "model"

    def __unicode__(self):
        try:
            return unicode(getattr(self, self.__label__))
        except AttributeError:
            return unicode(self.id)

class PostgresNativeUUIDField(UUIDField):
    """
    Improvement to django_extensions.db.fields.UUIDField to use postgres
    internal UUID field type rather than char for storage.
    
    """
    def db_type(self, connection=None):
        if connection and connection.vendor in ("postgresql",):
            return "UUID"
        return super(UUIDField, self).db_type(connection)

