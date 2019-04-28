from django.conf.urls import url
from django.contrib.admin import site
from django.urls import include
from django.views.decorators.csrf import csrf_exempt

from lippukala.views import POSView

urlpatterns = [
    url("^admin/", site.urls),
    url("^pos/$", csrf_exempt(POSView.as_view())),
]
