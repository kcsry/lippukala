import datetime
import json

from django.contrib.admin import site
from django.contrib.admin.options import ModelAdmin, TabularInline

from lippukala.consts import UNUSED
from lippukala.models import Code, Order

FIELDS_OF_EXTRA_INTEREST = {"status", "used_at", "used_on"}


class CodeInline(TabularInline):
    model = Code


class OrderAdmin(ModelAdmin):
    inlines = [CodeInline]
    search_fields = ["reference_number", "address_text", "comment"]
    list_filter = ["event"]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


def order_details(code):
    return f"{code.order.reference_number} ({code.order.address_text})"


order_details.short_description = "Order"  # type: ignore[attr-defined]


def maybe_stringify(val):
    if isinstance(val, (datetime.date, datetime.time, datetime.datetime)):
        return val.isoformat()
    if isinstance(val, (dict, list)):
        return json.dumps(val, default=str)
    return val


class CodeAdmin(ModelAdmin):
    search_fields = [
        "code",
        "literate_code",
        "order__reference_number",
        "order__address_text",
        "order__comment",
    ]
    readonly_fields = ["order", "code", "literate_code", "prefix", "product_text"]
    list_filter = ["order__event", "status"]
    list_display = ["status", "code", "literate_code", order_details]
    ordering = ["code"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("order")
        return qs

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj: Code, form, change):
        changed = set(form.changed_data)
        if changed & FIELDS_OF_EXTRA_INTEREST:
            old_values = Code.objects.filter(pk=obj.pk).values(*FIELDS_OF_EXTRA_INTEREST).first()
            obj._change_message_extra = {
                "lippukala": {
                    key: [maybe_stringify(old_value), maybe_stringify(getattr(obj, key))]
                    for (key, old_value) in old_values.items()
                    if old_value != getattr(obj, key)
                },
            }
        if obj.status == UNUSED:
            obj.used_at = ""
            obj.used_on = None
        super().save_model(request, obj, form, change)

    def construct_change_message(self, request, form, formsets, add=False):
        change_message = super().construct_change_message(request, form, formsets, add)
        if hasattr(form.instance, "_change_message_extra"):
            assert isinstance(change_message, list)
            change_message = [form.instance._change_message_extra, *change_message]
        return change_message


site.register(Order, OrderAdmin)
site.register(Code, CodeAdmin)
