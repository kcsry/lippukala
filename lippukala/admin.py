# -- encoding: UTF-8 --
from django.contrib.admin import site
from django.contrib.admin.options import TabularInline, ModelAdmin
from lippukala.models import Order, Code

class CodeInline(TabularInline):
	model = Code

class OrderAdmin(ModelAdmin):
	inlines = [CodeInline]

	def has_delete_permission(self, request, obj=None):
		return False

	def has_add_permission(self, request):
		return False

site.register(Order, OrderAdmin)