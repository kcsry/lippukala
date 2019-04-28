from django.contrib.admin import site
from django.contrib.admin.options import ModelAdmin, TabularInline

from lippukala.models import Code, Order


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
    return "%s (%s)" % (code.order.reference_number, code.order.address_text)
order_details.short_description = "Order"


class CodeAdmin(ModelAdmin):
    search_fields = ["code", "literate_code", "order__reference_number", "order__address_text", "order__comment"]
    readonly_fields = ["order", "code", "literate_code", "prefix", "product_text"]
    list_filter = ["order__event", "status"]
    list_display = ["status", "code", "literate_code", order_details]
    ordering = ["code"]

    def get_queryset(self, request):
        qs = super(CodeAdmin, self).get_queryset(request)
        qs = qs.select_related("order")
        return qs

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

site.register(Order, OrderAdmin)
site.register(Code, CodeAdmin)
