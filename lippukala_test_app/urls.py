from django.contrib.admin import site
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from lippukala.views import POSView

urlpatterns = [
    path('admin/', site.urls),
    path('pos/', csrf_exempt(POSView.as_view())),
]
