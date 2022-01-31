"""Rides views set"""

# Django
from django.shortcuts import get_object_or_404

# Models
from cride.circles.models import Circle

# Permission
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions.memberships import IsActiveCircleMember

# Django rest framework
from rest_framework import mixins, viewsets

# Serializers
from cride.rides.serializers import CreateRideSerializer

class RideViewSet(mixins.CreateModelMixin, 
                    viewsets.GenericViewSet):
    
    serializer_class = CreateRideSerializer
    permission_clasess = [IsAuthenticated, IsActiveCircleMember]

    def dispatch(self, request, *args, **kwargs):
        """Verify that the circle exist."""
        slug_name = kwargs['slug_name']
        self.circle = get_object_or_404(Circle, slug_name=slug_name)
        return super(RideViewSet, self).dispatch(request, *kwargs, **kwargs)
