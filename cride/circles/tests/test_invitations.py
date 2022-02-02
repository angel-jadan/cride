"""Invitation test."""

# Django
from django.test import TestCase

# Django REST Framework
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status

# Models
from cride.circles.models import Circle, Invitation, Membership
from cride.users.models import User, Profile


class InvitationManagerTestCase(TestCase):
    """Invitation Manager Test Case"""

    def setUp(self):
        """Test case setup."""
        self.user = User.objects.create(
            first_name='Angel',
            last_name='Jadan',
            email='angel_jadan@outlook.com',
            username='ajadan',
            password='ajadan1234',
        )
        self.circle = Circle.objects.create(
            name='Facultad de Ciencias',
            slug_name='fciencias',
            about='Grupo oficial de la Facultad de Ciencias de la UNAM',
            verify=True
        )

    def test_code_generation(self):
        """Random codes shoul be generated automatically."""
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
        )
        self.assertIsNotNone(invitation.code)

    def test_code_usage(self):
        """If a code is given, there's no need to create a new one."""
        code = 'holamundo'
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
            code=code
        )
        self.assertEqual(invitation.code, code)

    def test_code_generation_if_duplicated(self):
        """If given code is not unique, a new one must be generated."""
        code = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
        ).code

        # Create another invitation with the past code
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
            code=code
        )
        self.assertNotEqual(code, invitation.code)


class MemberInvitationsAPITestCase(APITestCase):
    """Member invitation API test case."""

    def setUp(self):
        """Test case setup."""
        self.user = User.objects.create(
            first_name='Angel',
            last_name='Jadan',
            email='angel_jadan@outlook.com',
            username='ajadan',
            password='ajadan1234',
        )
        self.profile = Profile.objects.create(user=self.user)
        self.circle = Circle.objects.create(
            name='Facultad de Ciencias',
            slug_name='fciencias',
            about='Grupo oficial de la Facultad de Ciencias de la UNAM',
            verify=True
        )
        self.membership = Membership.objects.create(
            user=self.user,
            profile=self.user.profile,
            circle=self.circle,
            remainig_invitations=10
        )
        self.token = Token.objects.create(user=self.user).key
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.token))
        self.url = '/circles/{}/members/{}/invitations/'.format(
            self.circle.slug_name,
            self.user.username
        )

    def test_response_success(self):
        """Verify request succed."""
        request = self.cliente.get(self.url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
    
    def test_invitation_creation(self):
        """Verify invitation are generated if none ixist previusly."""
        # Invitation in DB must be 0
        self.assertEqual(Invitation.objects.count(), 0)

        # Call member invitations URL
        request = self.cliente.get(self.url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        # Verify new invitations were created
        invitations = Invitation.objects.filter(issued_by=self.user)
        self.assertEqual(invitations.count(), self.membership.remainig_invitations)
        for invitation in invitations:
            self.assertIn(invitation.code, request.data['invitations'])
