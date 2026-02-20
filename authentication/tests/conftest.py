# conftest.py
import pytest
from rest_framework.test import APIClient
from authentication.factories import UserFactory

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_factory():
    return UserFactory

@pytest.fixture
def create_user(db, user_factory):
    def _create(username='testuser', password='ComplexPass123!'):
        return user_factory(username=username, password=password)
    return _create
