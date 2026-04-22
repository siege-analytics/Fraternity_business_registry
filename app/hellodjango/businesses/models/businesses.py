from __future__ import unicode_literals

from django.contrib.gis.db import models
from django.utils import timezone

from locations.models import United_States_Address

from .fraternities import Chapter, Fraternity


class BusinessCategory(models.Model):
    """
    Category/type of business (e.g. Restaurant, Retail, Professional Services).

    Kept as its own table so the taxonomy can be managed in the admin without
    a code change, and so the same category can be shared by many businesses.
    """

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "businesses_category"
        ordering = ["name"]
        verbose_name = "business category"
        verbose_name_plural = "business categories"

    def __str__(self):
        return self.name


class Business(models.Model):
    """
    A business owned, operated, or majority-controlled by one or more
    fraternity/sorority members, chapters, or the national organization.

    A single business can be associated with multiple fraternities or chapters
    (via ``BusinessOwnership``), which covers partnerships, multi-chapter
    investments, and businesses run by alumni from more than one organization.
    """

    class OwnershipClass(models.TextChoices):
        NATIONAL = "national", "Owned by National Organization"
        CHAPTER = "chapter", "Owned by Local Chapter"
        MEMBER = "member", "Owned by Individual Member(s)"
        ALUMNI_GROUP = "alumni_group", "Owned by Alumni Group"
        MIXED = "mixed", "Mixed / Multiple"

    class OperatingStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        CLOSED = "closed", "Closed"
        PENDING = "pending", "Pending Verification"
        SEASONAL = "seasonal", "Seasonal"

    name = models.CharField(max_length=250)
    legal_name = models.CharField(max_length=250, null=True, blank=True)
    dba = models.CharField(
        max_length=250, null=True, blank=True, help_text="Doing Business As"
    )
    description = models.TextField(null=True, blank=True)

    category = models.ForeignKey(
        BusinessCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="businesses",
    )

    ownership_class = models.CharField(
        max_length=32,
        choices=OwnershipClass.choices,
        default=OwnershipClass.MEMBER,
    )
    operating_status = models.CharField(
        max_length=16,
        choices=OperatingStatus.choices,
        default=OperatingStatus.ACTIVE,
    )

    year_founded = models.PositiveIntegerField(null=True, blank=True)
    employee_count = models.PositiveIntegerField(null=True, blank=True)

    # Contact
    website = models.URLField(max_length=500, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    phone = models.CharField(max_length=32, null=True, blank=True)

    # Location
    address = models.ForeignKey(
        United_States_Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="businesses",
    )
    geom = models.PointField(srid=4326, null=True, blank=True)

    # Verification / registry metadata
    verified = models.BooleanField(
        default=False,
        help_text="Whether the fraternity ownership has been confirmed.",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "businesses_business"
        ordering = ["name"]
        verbose_name = "business"
        verbose_name_plural = "businesses"
        indexes = [
            models.Index(fields=["ownership_class"]),
            models.Index(fields=["operating_status"]),
            models.Index(fields=["verified"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return self.name


class BusinessOwnership(models.Model):
    """
    Links a Business to the fraternities, chapters, or named members that own
    or control it. One business can have multiple ownership rows to represent
    partnerships and multi-fraternity ownership.
    """

    class OwnerRole(models.TextChoices):
        FOUNDER = "founder", "Founder"
        OWNER = "owner", "Owner"
        CO_OWNER = "co_owner", "Co-Owner"
        INVESTOR = "investor", "Investor"
        OPERATOR = "operator", "Operator"

    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="ownerships"
    )
    fraternity = models.ForeignKey(
        Fraternity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="business_ownerships",
    )
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="business_ownerships",
    )
    member_name = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text="Individual member's name, if ownership is held by a person.",
    )
    role = models.CharField(
        max_length=32, choices=OwnerRole.choices, default=OwnerRole.OWNER
    )
    ownership_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage of ownership (0.00 - 100.00), optional.",
    )
    since = models.DateField(null=True, blank=True)
    until = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "businesses_ownership"
        ordering = ["-since", "role"]
        verbose_name = "business ownership"
        verbose_name_plural = "business ownerships"
        indexes = [
            models.Index(fields=["fraternity"]),
            models.Index(fields=["chapter"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(fraternity__isnull=False)
                    | models.Q(chapter__isnull=False)
                    | models.Q(member_name__isnull=False)
                ),
                name="ownership_has_at_least_one_owner",
            ),
        ]

    def __str__(self):
        owner = (
            (self.chapter and str(self.chapter))
            or (self.fraternity and str(self.fraternity))
            or self.member_name
            or "Unknown"
        )
        return f"{owner} — {self.get_role_display()} of {self.business.name}"
