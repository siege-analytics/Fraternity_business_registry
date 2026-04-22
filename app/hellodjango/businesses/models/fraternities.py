from __future__ import unicode_literals

from django.contrib.gis.db import models
from django.utils import timezone

from locations.models import United_States_Address


class Council(models.Model):
    """
    Umbrella governing council for Greek-letter organizations.

    Common examples:
      - NIC  (North American Interfraternity Conference)
      - NPC  (National Panhellenic Conference)
      - NPHC (National Pan-Hellenic Council, "Divine Nine")
      - NALFO (National Association of Latino Fraternal Organizations)
      - NAPA (National APIDA Panhellenic Association)
      - NMGC (National Multicultural Greek Council)
      - PFA  (Professional Fraternity Association)
    """

    abbreviation = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=250)
    website = models.URLField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = "businesses_council"
        ordering = ["abbreviation"]
        verbose_name = "council"
        verbose_name_plural = "councils"

    def __str__(self):
        return f"{self.abbreviation} - {self.name}"


class Fraternity(models.Model):
    """
    A Greek-letter organization (social fraternity, sorority, professional,
    honor, service, etc.) recognized at the national/international level.

    The ``fraternity_type`` distinguishes social from professional/honor/etc.,
    and ``council`` captures which umbrella body it sits under.
    """

    class FraternityType(models.TextChoices):
        SOCIAL_FRATERNITY = "social_fraternity", "Social Fraternity"
        SOCIAL_SORORITY = "social_sorority", "Social Sorority"
        PROFESSIONAL = "professional", "Professional"
        HONOR = "honor", "Honor Society"
        SERVICE = "service", "Service"
        RELIGIOUS = "religious", "Religious"
        MULTICULTURAL = "multicultural", "Multicultural"
        OTHER = "other", "Other"

    name = models.CharField(max_length=250, unique=True)
    greek_letters = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="Greek letter designation, e.g. 'ΑΦΑ' or 'Alpha Phi Alpha'",
    )
    nickname = models.CharField(max_length=250, null=True, blank=True)
    fraternity_type = models.CharField(
        max_length=32,
        choices=FraternityType.choices,
        default=FraternityType.SOCIAL_FRATERNITY,
    )
    council = models.ForeignKey(
        Council,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fraternities",
    )
    year_founded = models.PositiveIntegerField(null=True, blank=True)
    founding_institution = models.CharField(max_length=250, null=True, blank=True)
    website = models.URLField(max_length=500, null=True, blank=True)
    headquarters_address = models.ForeignKey(
        United_States_Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fraternity_headquarters",
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "businesses_fraternity"
        ordering = ["name"]
        verbose_name = "fraternity"
        verbose_name_plural = "fraternities"
        indexes = [
            models.Index(fields=["fraternity_type"]),
            models.Index(fields=["council"]),
        ]

    def __str__(self):
        if self.greek_letters:
            return f"{self.name} ({self.greek_letters})"
        return self.name


class Chapter(models.Model):
    """
    A local chapter of a Fraternity.

    Chapters may be collegiate (attached to an institution) or alumni/city
    chapters. The ``designation`` is the Greek-letter chapter name (e.g.
    'Alpha', 'Beta Gamma'); the ``institution`` captures the college or city
    the chapter serves.
    """

    class ChapterStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        SUSPENDED = "suspended", "Suspended"
        COLONY = "colony", "Colony / Provisional"
        ALUMNI = "alumni", "Alumni / Graduate"

    fraternity = models.ForeignKey(
        Fraternity, on_delete=models.CASCADE, related_name="chapters"
    )
    designation = models.CharField(
        max_length=120,
        help_text="Chapter Greek-letter designation, e.g. 'Alpha' or 'Beta Gamma'",
    )
    institution = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text="Host college/university, or city for alumni chapters",
    )
    status = models.CharField(
        max_length=16, choices=ChapterStatus.choices, default=ChapterStatus.ACTIVE
    )
    year_chartered = models.PositiveIntegerField(null=True, blank=True)
    address = models.ForeignKey(
        United_States_Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chapters",
    )
    # Chapter house point (if it has a physical house)
    geom = models.PointField(srid=4326, null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "businesses_chapter"
        ordering = ["fraternity__name", "designation"]
        verbose_name = "chapter"
        verbose_name_plural = "chapters"
        constraints = [
            models.UniqueConstraint(
                fields=["fraternity", "designation", "institution"],
                name="unique_chapter_per_fraternity_institution",
            ),
        ]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["institution"]),
        ]

    def __str__(self):
        parts = [self.fraternity.name, self.designation]
        if self.institution:
            parts.append(f"@ {self.institution}")
        return " ".join(parts)
