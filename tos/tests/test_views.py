from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

# Django 1.4 compatability
try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
    get_user_model = lambda: User

from tos.models import TermsOfService, UserAgreement, has_user_agreed_latest_tos, USER_MODEL as USER

class TestViews(TestCase):

    def setUp(self):
        self.user1 = USER.objects.create_user('user1', 'user1@example.com', 'user1pass')
        self.user2 = USER.objects.create_user('user2', 'user2@example.com', 'user2pass')

        self.tos1 = TermsOfService.objects.create(
            content="first edition of the terms of service",
            active=True
        )
        self.tos2 = TermsOfService.objects.create(
            content="second edition of the terms of service",
            active=False
        )

        self.check_tos_url = reverse('tos_check_tos')

        UserAgreement.objects.create(
            terms_of_service=self.tos1,
            user=self.user1
        )

    def test_need_agreement(self):
        """ user2 tries to login and then has to go and agree to terms"""

        self.assertFalse(has_user_agreed_latest_tos(self.user2))

        self.client.login(username='user2', password='user2pass')

        response = self.client.post(self.check_tos_url)
        self.assertContains(response, "first edition of the terms of service")

        self.assertFalse(has_user_agreed_latest_tos(self.user2))

    def test_does_not_need_agreement(self):
        self.assertTrue(has_user_agreed_latest_tos(self.user1))

        self.client.login(username='user1', password='user1pass')

        response = self.client.post(self.check_tos_url)

        self.assertTrue(has_user_agreed_latest_tos(self.user1))

    def test_reject_agreement(self):

        self.assertFalse(has_user_agreed_latest_tos(self.user2))

        self.client.login(username='user2', password='user2pass')

        url = reverse('tos_check_tos')
        response = self.client.post(url, {'accept': 'reject'})

        self.assertFalse(has_user_agreed_latest_tos(self.user2))

    def test_accept_agreement(self):

        self.assertFalse(has_user_agreed_latest_tos(self.user2))

        self.client.login(username='user2', password='user2pass')

        url = reverse('tos_check_tos')
        response = self.client.post(url, {'accept': 'accept'})

        self.assertTrue(has_user_agreed_latest_tos(self.user2))

    def test_bump_new_agreement(self):
        self.assertFalse(has_user_agreed_latest_tos(self.user2))

        self.client.login(username='user2', password='user2pass')

        url = reverse('tos_check_tos')
        response = self.client.post(url, {'accept': 'accept'})

        self.assertTrue(has_user_agreed_latest_tos(self.user2))

        self.tos2.active = True
        self.tos2.save()
        self.tos1.active = False
        self.tos1.save()

        self.assertFalse(has_user_agreed_latest_tos(self.user2))

        url = reverse('tos_check_tos')
        response = self.client.post(url, {'accept': 'accept'})

        self.assertTrue(has_user_agreed_latest_tos(self.user2))
