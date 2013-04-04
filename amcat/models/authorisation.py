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
Module containing classes and utility functions related to AmCAT authorisation

Main entry points are

check(db, privilege/str/int) checks whether user has privilege
getPrivilege(db, str or int) returns Privilege object

"""
from django.db import models
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied

from amcat.models.project import Project
from amcat.tools.model import AmcatProjectModel
from amcat.tools.caching import cached

AMCAT_APP_LABEL = "amcat"

class ProjectModelBackend(object):
    """
    This is an authorisation backend which takes an Project as `obj` and
    tries to evaluate whether the user has the permission requested.
    """
    @property
    @classmethod
    @cached
    def permissions(cls):
        """Provides a dictionary mapping all possible ids with their codenames"""
        return dict(Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Project),
            codename__in=dict(Project._meta.permissions).keys()
        ).values("codename", "id"))

    def has_perm(self, user_obj, perm, obj=None):
        if not isinstance(obj, Project):
            # We can't provide any information about non-project permissions
            return None

        # Check for existence. If permission does not exist, deny access.
        if perm not in self.permissions.keys():
            raise PermissionDenied

        # Retrieving all permission objects for this user and project prevents
        # multiple roundtrips to the database.
        try:
            has_perm = (ProjectPermission.objects.select_related("permission")
                            .get(project=obj, user=user_obj).permission)
        except ProjectPermission.DoesNotExist:
            # User has no privileges on this project, so he's a guest. If no guest_role
            # is set, this project is not readable for non-members.
            if not obj.guest_role:
                raise PermissionDenied

            has_perm = obj.guest_role

        # Check whether user has the permissions needed based on id
        has_perm_id = self.permissions.get(has_perm.codename)
        needs_perm_id = self.permissions.get(perm.codename)

        if has_perm_id >= needs_perm_id:
            return True

        raise PermissionDenied


class ProjectPermission(AmcatProjectModel):
    project = models.ForeignKey("amcat.Project", db_index=True)
    user = models.ForeignKey(User, db_index=True)

    # MUST be one of the permissions defined in Project._meta.permissions, but
    # I'm not sure how we can force this behaviour.
    permission = models.ForeignKey(Permission, null=True)

    def __unicode__(self):
        return u"%s, %s" % (self.project, self.permission)

    class Meta():
        db_table = 'projects_users_permissions'
        unique_together = ("project", "user")
        app_label = 'amcat'

