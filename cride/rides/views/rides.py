"""Rides views set"""

# Django
from datetime import timedelta
from functools import partial
import re
from django.template import context
from django.utils import timezone

# Models
from cride.circles.models import Circle

# Permission
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions.memberships import IsActiveCircleMember
from cride.rides.permissions.rides import IsRideOwner, IsNotRideOwner

# Filter
from rest_framework.filters import SearchFilter, OrderingFilter

# Django rest framework
from rest_framework import mixins, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework import status

# Serializers
from cride.rides.serializers import(
    CreateRideSerializer,
    RideModelSerializer,
    JoinRideSerializer,
    EndRideSerializer,
    CreateRideRatingSerializer
)


class RideViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """Ride view set."""

    filter_backends = (SearchFilter, OrderingFilter)
    ordering = ('departure_date', 'arrival_date', 'available_seats')
    ordering_fields = ('deaprture_date', 'arrival_date', 'availabel_seats')
    search_fields = ('deaprture_location', 'arrival_location')

    def dispatch(self, request, *args, **kwargs):
        """Verify that the circle exist."""
        slug_name = kwargs['slug_name']
        self.circle = get_object_or_404(Circle, slug_name=slug_name)
        return super(RideViewSet, self).dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """Assign permission based on action."""
        permissions = [IsAuthenticated, IsActiveCircleMember]
        if self.action in ['update', 'partial_update', 'finish']:
            permissions.append(IsRideOwner)
        if self.action == 'join':
            permissions.append(IsNotRideOwner)
        return [p() for p in permissions]

    def get_serializer_context(self):
        """Add circle to serializer context."""
        context = super(RideViewSet, self).get_serializer_context()
        context['circle'] = self.circle
        return context

    def get_serializer_class(self):
        """Return serializer based on action."""
        if self.action == 'create':
            return CreateRideSerializer
        if self.action == 'update':
            return JoinRideSerializer
        if self.action == 'finish':
            return EndRideSerializer
        if self.action == 'rate':
                return CreateRideRatingSerializer
        return RideModelSerializer

    def get_queryset(self):
        """Return active circle's rides."""
        offest = timezone.now() + timedelta(minutes=10)
        if self.action not in ['finish', 'retrieve']:
            return self.circle.ride_set.filter(
                departure_date__gte=offest,
                is_active=True,
                available_seats__gte=1
            )
        return self.circle.ride_set.all()

    @action(detail=True, methods=['post'])
    def join(self, request, *args, **kwargs):
        """Add requesting user to ride."""
        ride = self.get_object()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            ride,
            data={'passenger': request.user.pk},
            context={'ride': ride, 'circle': self.circle},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        ride = serializer.save()
        data = RideModelSerializer(ride).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def finish(self, request, *args, **kwargs):
        """Add requesting user to ride."""
        ride = self.get_object()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            ride,
            data={'is_active': False, 'current_time': timezone.now()},
            context=self.get_serializer_context(),
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        ride = serializer.save()
        data = RideModelSerializer(ride).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def rate(self, request, *args, **kwargs):
        """Rate ride"""
        ride = self.get_object()
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        context['ride'] = ride
        serializer = serializer_class(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        ride = serializer.save()
        data = RideModelSerializer(ride).data
        return Response(data, status=status.HTTP_201_CREATED)
