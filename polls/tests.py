from unittest.mock import patch

from celery.exceptions import Retry
from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from polls.factories import UserFactory

from polls.tasks import task_add_subscribe


class UserSubscribeViewTestCase(TestCase):
    @patch("polls.views.task_add_subscribe.delay")
    def test_subscribe_post_succeed(self, mock_task_add_subscribe_delay):
        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            response = self.client.post(
                reverse("user_subscribe"),
                {"username": "test", "email": "test@gmail.com"},
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.filter(username="test").exists(), True)

        self.assertEqual(len(callbacks), 1)

        user = User.objects.filter(username="test").first()
        mock_task_add_subscribe_delay.assert_called_with(user.pk)


class TaskAddSubscribeTest(TestCase):
    """
    Only tests the Celery task
    """

    @patch("polls.tasks.requests.post")
    def test_post_succeed(self, mock_requests_post):
        instance = UserFactory.create()
        task_add_subscribe(instance.pk)

        mock_requests_post.assert_called_with(
            "https://httpbin.org/delay/5", data={"email": instance.email}
        )

    @patch("polls.tasks.task_add_subscribe.retry")
    @patch("polls.tasks.requests.post")
    def test_exception(self, mock_requests_post, mock_task_add_subscribe_retry):
        mock_requests_post.side_effect = Exception()
        mock_task_add_subscribe_retry.side_effect = Retry()

        instance = UserFactory.create()

        with self.assertRaises(Retry):
            task_add_subscribe(instance.pk)
