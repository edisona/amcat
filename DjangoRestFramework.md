# Introduction #

Django Rest Framework uses a quite complicated design with many subclasses and mixins from its own codebase and from django.views. Since I often ahve difficulty understanding exactly what happens where, I decided to write it down in a wiki page.

# Basic structure #

(I use `rf.` for `rest_framework`, and `d.` for `django.`

In Django Rest Framework, requests are handled by views which directly inherit from django views. A lot of the hard work is done by serializers.


Our API views generally inherit from `rf.generics.ListAPIView`. Inheritance structure:

  * `api.rest.resources.amcatresource.AmCATResource`
    * `rf.generics.ListAPIView`
      * `rf.mixins.ListModelMixin`
      * `rf.generics.MultipleObjectAPIView`
        * `d.views.generic.list.MultipleObjectMixin`
        * `rf.generics.GenericAPIView`
          * `rf.views.APIView`
          * `d.views.generic.View` (via compat)

Next to this, we have a default filter backend and serializers:
  * `api.rest.filters.AmCATFilterBackend`
    * `rf.filters.DjangoFilterBackend`
  * `AutoFilterSet` (inner class in AmCATFilterBackend)
    * `django_filters.filterset`

  * `api.rest.serializer.AmCATModelSerializer`
    * `rf.serializers.ModelSerializer`
      * `rf.serializers.Serializer`
        * `rf.serializers.BaseSerializer`

  * `api.rest.serializer.AmCATPaginationSerializer`
    * `rf.pagination.BasePaginationSerializer`
      * `rf.serializers.Serializer`
        * `rf.serializers.BaseSerializer`


AmCATPaginationSerializer(pagination.BasePaginationSerializer)

APIView defines the view dispatch, which simply calls the get/post etc method on the view object. The following sections describe how these requests are handled:

## GET requests ##

  * `ListAPIView`.get() calls list()
  * `ListModelMixin`.list() calls get\_queryset, filter\_queryset, get\_paginate\_by [settings](from.md) && paginate\_queryset, and finally get_[pagination_]serializer and returns serializer.data
    1. `MultipleObjectMixin`.get\_queryset() returns self.model.objects.all()
    1. `MultipleObjectAPIView`.filter\_queryset calls self.filter\_backend.filter\_queryset().
      * `AmCATFilterBackend` [defined in settings.py](as.md) returns  `AutoFilterSet`(django\_filters.filterset.FilterSet)
      * `AutoFilterSet` acts like a queryset object, with iter, len, and getitem methods, and calls _filter and_order\_by using the GET parameters
    1. `MultipleObjectAPIView`.get\_paginate\_by returns the page\_size GET parameter or the default 10 (from settings.py)
    1. `MultipleObjectMixin`.paginate\_queryset uses (by default) a `django.core.paginator.Paginator`, which uses slicing on the queryset to get a 'page'
    1. `MultipleObjectAPIView`.get\_pagination\_serializer and `GenericAPIView`.get\_serializer use the serializerclass from settings, set to 'AmCATPaginationSerializer' and 'AmCATModelSerializer' respectivel. The pagination serializer calls get normal get\_serializer again to set the object\_serializer, so ultimately the objects are all serialized by the `AmCATModelSerializer`
  * `BaseSerializer`.data is a cached property that calls to\_native, which calls convert\_object
  * `BaseSerializer`.convert\_object basically calls `field_to_native(field) for field in self.get_fields()`
    * `BaseSerializer`.get\_fields returns any fields declared as class properties, plus get\_default\_fields
    * `ModelSerializer`.get\_default\_fields gets the fields from the model
  * `BaseSerializer`.field\_to\_native uses getattr(obj, field), and calls to\_native in the resulting object.


Places for customization:

  * Many classes have class fields that define behaviour:
    * `MultipleObjectAPIView` defines paginate\_by (and related) and  filter\_backend
    * `MultipleObjectMixin` defines paginator\_class
