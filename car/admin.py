from django.contrib import admin
from .models import CarContent


@admin.register(CarContent)
class CarContentAdmin(admin.ModelAdmin):
    list_display = ("title", "condition", "color", "body_type", "fuel_type", "price_range","user")
    list_filter = ("condition", "color", "body_type", "fuel_type", "price_range")
    search_fields = ("title", "description")
    readonly_fields = ()
