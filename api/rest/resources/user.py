from amcat.models import User

from api.rest.resources.amcatresource import AmCATResource
from api.rest.serializer import AmCATModelSerializer

class UserSerializer(AmCATModelSerializer):
    class Meta:
        model = User
        exclude = ("password", "email")

class UserResource(AmCATResource):
    model = User
    extra_filters = ["userprofile__affiliation__id"]
    serializer_class = UserSerializer

    @classmethod
    def get_label(cls):
        return "{username}"
