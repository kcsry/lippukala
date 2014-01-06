# -*- coding: utf-8 -*-
from django.http import HttpResponse

try:
    import json
except ImportError:
    import django.utils.simplejson as json

from django.views.generic import TemplateView
from lippukala.models import Code, CantUseException


def serialize_code(code):
    return {
        "id": code.id,
        "used": bool(code.used_at),
        "code": code.code,
        "lit": code.literate_code,
        "name": code.order.address_text,
        "comment": code.order.comment,
        "prod": code.product_text,
    }

class POSView(TemplateView):
    template_name = "lippukala/pos.html"

    def get_valid_codes(self, request):
        event_filter = request.GET.get("event")
        qs = Code.objects.all().select_related("order")
        if event_filter:
            qs = qs.filter(event=event_filter)
        return qs

    def get_json(self, request):
        qs = self.get_valid_codes(request)
        data = [serialize_code(code) for code in qs.iterator()]
        json_data = json.dumps({"codes": data})
        return HttpResponse(json_data, content_type="application/json")

    def get(self, request, *args, **kwargs):
        if request.GET.get("json"):
            return self.get_json(request)
        return super(POSView, self).get(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        json_data = '{"what": true}'
        if request.REQUEST.get("use"):
            station = request.REQUEST.get("station") or "(n/a)"
            ids = [int(s, 10) for s in request.REQUEST.get("use").split(",")]
            codes = []
            qs = self.get_valid_codes(request)
            for id in ids:
                code = qs.get(pk=id)
                try:
                    code.set_used(used_at=station)
                except CantUseException:
                    pass
                codes.append(code)
            data = [serialize_code(code) for code in codes]
            json_data = json.dumps({"codes": data})
        return HttpResponse(json_data, content_type="application/json")