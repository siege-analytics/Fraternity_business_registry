from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from rest_framework import generics
from rest_framework_gis.pagination import GeoJsonPagination

from businesses.models import Business, BusinessCategory, BusinessOwnership
from businesses.serializers import (
    BusinessCategorySerializer,
    BusinessOwnershipSerializer,
    BusinessSerializer,
)


class BusinessCategoryList(generics.ListCreateAPIView):
    queryset = BusinessCategory.objects.all()
    serializer_class = BusinessCategorySerializer


class BusinessCategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = BusinessCategory.objects.all()
    serializer_class = BusinessCategorySerializer


class BusinessList(generics.ListCreateAPIView):
    queryset = (
        Business.objects.select_related("category", "address")
        .prefetch_related("ownerships__fraternity", "ownerships__chapter")
        .all()
    )
    serializer_class = BusinessSerializer
    pagination_class = GeoJsonPagination
    filterset_fields = [
        "category",
        "ownership_class",
        "operating_status",
        "verified",
    ]


class BusinessDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = (
        Business.objects.select_related("category", "address")
        .prefetch_related("ownerships__fraternity", "ownerships__chapter")
        .all()
    )
    serializer_class = BusinessSerializer


class BusinessNearbyList(generics.ListAPIView):
    """
    GET /businesses/businesses/nearby/?lat=37.77&lon=-122.41&radius_km=10

    Returns verified, active businesses within ``radius_km`` of the given
    point, ordered by distance.
    """

    serializer_class = BusinessSerializer
    pagination_class = GeoJsonPagination

    def get_queryset(self):
        qs = Business.objects.select_related("category", "address").filter(
            geom__isnull=False
        )
        lat = self.request.query_params.get("lat")
        lon = self.request.query_params.get("lon")
        radius_km = self.request.query_params.get("radius_km", "25")
        if lat is None or lon is None:
            return qs.none()
        try:
            point = Point(float(lon), float(lat), srid=4326)
            radius = float(radius_km)
        except (TypeError, ValueError):
            return qs.none()
        return qs.filter(geom__distance_lte=(point, D(km=radius))).order_by("geom")


class BusinessOwnershipList(generics.ListCreateAPIView):
    queryset = BusinessOwnership.objects.select_related(
        "business", "fraternity", "chapter"
    ).all()
    serializer_class = BusinessOwnershipSerializer
    filterset_fields = ["business", "fraternity", "chapter", "role"]


class BusinessOwnershipDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = BusinessOwnership.objects.select_related(
        "business", "fraternity", "chapter"
    ).all()
    serializer_class = BusinessOwnershipSerializer
