"""Circles admin."""

# Django
from asyncore import write
from django.contrib import admin

# Django REST Framework
from rest_framework import status

# Model
from cride.circles.models import Circle
from cride.rides.models import Ride
from django.http import HttpResponse

# Utilities
import csv
from django.utils import timezone
from datetime import datetime, timedelta


@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    """Circle admin."""

    list_display = (
        'slug_name',
        'name',
        'is_public',
        'verified',
        'is_limited',
        'members_limit'
    )
    search_fields = ('slug_name', 'name')
    list_filter = (
        'is_public',
        'verified',
        'is_limited'
    )

    actions = ['make_verified', 'make_unverified', 'download_todays_rides']

    def make_verified(self, request, queryset):
        """Make circle verifyed"""
        queryset.update(verified=True)
    make_verified_description = 'Make selected circles verified'

    def make_unverified(self, request, queryset):
        """Make circle unverifyed"""
        queryset.update(verified=False)
    make_unverified_description = 'Make selected circles verified'

    def download_todays_rides(self, request, queryset):
        """Return today's rides."""
        now = timezone.now()
        start = datetime(now.year, now.month, now.day, 0, 0, 0)
        end = start + timedelta(days=1)
        rides = Ride.objects.filter(
            offered_in__in=queryset.values_list(('id')),
            departure_date__gte=start,
            departure_date__lte=end
        ).order_by('departure_date')

        response_http = HttpResponse(content_type='text/csv')
        response_http['Content-Disposition'] = 'attachment; filename="Rides.csv"'
        writer = csv.writer(response_http)
        writer.writerow([
            'id',
            'passengers',
            'departure_location',
            'departure_date',
            'arrival_location',
            'arrival_date',
            'rating',
            ])
        for ride in rides:
            writer.writerow([
                ride.pk,
                ride.passengers.count(),
                ride.departure_location,
                str(ride.departure_date),
                ride.arrival_location,
                str(ride.arrival_date),
                ride.rating,
            ])

        return response_http
    download_todays_rides_description = 'Download todays rides'
