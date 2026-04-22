from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from businesses.models import (
    Business,
    BusinessCategory,
    BusinessOwnership,
    Chapter,
    Council,
    Fraternity,
)


@admin.register(Council)
class CouncilAdmin(admin.ModelAdmin):
    list_display = ("abbreviation", "name", "website")
    search_fields = ("abbreviation", "name")


@admin.register(Fraternity)
class FraternityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "greek_letters",
        "fraternity_type",
        "council",
        "year_founded",
    )
    list_filter = ("fraternity_type", "council")
    search_fields = ("name", "greek_letters", "nickname")


@admin.register(Chapter)
class ChapterAdmin(GISModelAdmin):
    list_display = (
        "fraternity",
        "designation",
        "institution",
        "status",
        "year_chartered",
    )
    list_filter = ("status", "fraternity")
    search_fields = ("designation", "institution", "fraternity__name")


@admin.register(BusinessCategory)
class BusinessCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class BusinessOwnershipInline(admin.TabularInline):
    model = BusinessOwnership
    extra = 1
    autocomplete_fields = ("fraternity", "chapter")


@admin.register(Business)
class BusinessAdmin(GISModelAdmin):
    list_display = (
        "name",
        "category",
        "ownership_class",
        "operating_status",
        "verified",
        "year_founded",
    )
    list_filter = (
        "ownership_class",
        "operating_status",
        "verified",
        "category",
    )
    search_fields = ("name", "legal_name", "dba", "email", "phone")
    inlines = [BusinessOwnershipInline]


@admin.register(BusinessOwnership)
class BusinessOwnershipAdmin(admin.ModelAdmin):
    list_display = (
        "business",
        "fraternity",
        "chapter",
        "member_name",
        "role",
        "ownership_percentage",
    )
    list_filter = ("role", "fraternity")
    search_fields = (
        "business__name",
        "fraternity__name",
        "chapter__designation",
        "member_name",
    )
