from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from businesses.models import (
    Business,
    BusinessCategory,
    BusinessOwnership,
    Chapter,
    Fraternity,
)


class BusinessCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessCategory
        fields = ["id", "name", "slug", "parent", "description"]


class BusinessOwnershipSerializer(serializers.ModelSerializer):
    fraternity_name = serializers.CharField(
        source="fraternity.name", read_only=True, default=None
    )
    chapter_name = serializers.CharField(
        source="chapter.__str__", read_only=True, default=None
    )

    class Meta:
        model = BusinessOwnership
        fields = [
            "id",
            "business",
            "fraternity",
            "fraternity_name",
            "chapter",
            "chapter_name",
            "member_name",
            "role",
            "ownership_percentage",
            "since",
            "until",
            "notes",
        ]


class BusinessSerializer(GeoFeatureModelSerializer):
    category = BusinessCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=BusinessCategory.objects.all(),
        source="category",
        write_only=True,
        required=False,
        allow_null=True,
    )
    ownerships = BusinessOwnershipSerializer(many=True, read_only=True)

    class Meta:
        model = Business
        geo_field = "geom"
        fields = [
            "id",
            "name",
            "legal_name",
            "dba",
            "description",
            "category",
            "category_id",
            "ownership_class",
            "operating_status",
            "year_founded",
            "employee_count",
            "website",
            "email",
            "phone",
            "address",
            "verified",
            "verified_at",
            "verification_notes",
            "ownerships",
            "created_at",
            "updated_at",
        ]
