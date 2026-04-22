from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from businesses import views


fraternity_urls = [
    path("councils/", views.CouncilList.as_view(), name="council_list"),
    path("councils/<int:pk>/", views.CouncilDetail.as_view(), name="council_detail"),
    path("fraternities/", views.FraternityList.as_view(), name="fraternity_list"),
    path(
        "fraternities/<int:pk>/",
        views.FraternityDetail.as_view(),
        name="fraternity_detail",
    ),
    path("chapters/", views.ChapterList.as_view(), name="chapter_list"),
    path("chapters/<int:pk>/", views.ChapterDetail.as_view(), name="chapter_detail"),
]

business_urls = [
    path(
        "categories/",
        views.BusinessCategoryList.as_view(),
        name="business_category_list",
    ),
    path(
        "categories/<int:pk>/",
        views.BusinessCategoryDetail.as_view(),
        name="business_category_detail",
    ),
    path("businesses/", views.BusinessList.as_view(), name="business_list"),
    path(
        "businesses/nearby/",
        views.BusinessNearbyList.as_view(),
        name="business_nearby",
    ),
    path(
        "businesses/<int:pk>/",
        views.BusinessDetail.as_view(),
        name="business_detail",
    ),
    path(
        "ownerships/",
        views.BusinessOwnershipList.as_view(),
        name="business_ownership_list",
    ),
    path(
        "ownerships/<int:pk>/",
        views.BusinessOwnershipDetail.as_view(),
        name="business_ownership_detail",
    ),
]

urlpatterns = fraternity_urls + business_urls
urlpatterns = format_suffix_patterns(urlpatterns)
