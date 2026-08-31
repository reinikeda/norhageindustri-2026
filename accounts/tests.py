from django.contrib.auth import get_user_model
from django.test import TestCase


class AccountsTests(TestCase):
    def test_custom_user_model(self):
        self.assertEqual(get_user_model()._meta.label, "accounts.User")

    def test_staff_user_can_be_created(self):
        User = get_user_model()
        user = User.objects.create_user(username="editor", password="test-pass-123")
        self.assertTrue(user.check_password("test-pass-123"))
        self.assertFalse(user.is_superuser)
