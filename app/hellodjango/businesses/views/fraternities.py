from rest_framework import generics

from businesses.models import Chapter, Council, Fraternity
from businesses.serializers import (
    ChapterSerializer,
    CouncilSerializer,
    FraternitySerializer,
)


class CouncilList(generics.ListCreateAPIView):
    queryset = Council.objects.all()
    serializer_class = CouncilSerializer


class CouncilDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Council.objects.all()
    serializer_class = CouncilSerializer


class FraternityList(generics.ListCreateAPIView):
    queryset = Fraternity.objects.select_related("council").all()
    serializer_class = FraternitySerializer
    filterset_fields = ["fraternity_type", "council"]


class FraternityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Fraternity.objects.select_related("council").all()
    serializer_class = FraternitySerializer


class ChapterList(generics.ListCreateAPIView):
    queryset = Chapter.objects.select_related("fraternity", "address").all()
    serializer_class = ChapterSerializer
    filterset_fields = ["fraternity", "status", "institution"]


class ChapterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chapter.objects.select_related("fraternity", "address").all()
    serializer_class = ChapterSerializer
