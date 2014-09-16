# -- encoding: UTF-8 --
from django.contrib.admin import site
from django.contrib.admin.options import TabularInline, ModelAdmin

from lippukala.models import Order, Code


class CodeInline(TabularInline):
    model = Code


class OrderAdmin(ModelAdmin):
    inlines = [CodeInline]
    search_fields = ["reference_number", "address_text", "comment"]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


def order_details(code):
    return "%s (%s)" % (code.order.reference_number, code.order.address_text)
order_details.short_description = u"Order"


class CodeAdmin(ModelAdmin):
    search_fields = ["code", "literate_code", "order__reference_number", "order__address_text", "order__comment"]
    readonly_fields = ["order", "code", "literate_code", "prefix", "product_text"]
    list_filter = ["status"]
    list_display = ["status", "code", "literate_code", order_details]
    ordering = ["code"]

    def get_queryset(self, request):
        qs = super(CodeAdmin, self).queryset(request)
        qs = qs.select_related("order")
        return qs

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

site.register(Order, OrderAdmin)
site.register(Code, CodeAdmin)
