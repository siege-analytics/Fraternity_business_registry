from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from businesses.models import Chapter, Council, Fraternity


class CouncilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Council
        fields = ["id", "abbreviation", "name", "website"]


class FraternitySerializer(serializers.ModelSerializer):
    council = CouncilSerializer(read_only=True)
    council_id = serializers.PrimaryKeyRelatedField(
        queryset=Council.objects.all(),
        source="council",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Fraternity
        fields = [
            "id",
            "name",
            "greek_letters",
            "nickname",
            "fraternity_type",
            "council",
            "council_id",
            "year_founded",
            "founding_institution",
            "website",
            "headquarters_address",
            "created_at",
            "updated_at",
        ]


class ChapterSerializer(GeoFeatureModelSerializer):
    fraternity = FraternitySerializer(read_only=True)
    fraternity_id = serializers.PrimaryKeyRelatedField(
        queryset=Fraternity.objects.all(), source="fraternity", write_only=True
    )

    class Meta:
        model = Chapter
        geo_field = "geom"
        fields = [
            "id",
            "fraternity",
            "fraternity_id",
            "designation",
            "institution",
            "status",
            "year_chartered",
            "address",
            "created_at",
            "updated_at",
        ]
