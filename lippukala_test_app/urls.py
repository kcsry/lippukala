from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from lippukala.views import POSView

urlpatterns = [
    url("^pos/$", csrf_exempt(POSView.as_view())),
]
