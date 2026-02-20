# authentication/tests/test_auth_api.py
import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
def test_register_creates_user_and_profile(api_client):
    url = reverse('register')
    payload = {
        "username": "pytestuser",
        "email": "pytestuser@example.com",
        "password": "ComplexPass123!",
        "password2": "ComplexPass123!"
    }

    resp = api_client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data['username'] == 'pytestuser'
    assert 'password' not in data

    # confirm profile exists (Profile signal should create it)
    from django.contrib.auth.models import User
    u = User.objects.get(username='pytestuser')
    assert hasattr(u, 'profile')
    assert u.profile.role == 'REPORTER'


@pytest.mark.django_db
def test_login_returns_tokens_and_me_works(api_client, create_user):
    # create a user with known password
    user = create_user(username='bob', password='ComplexPass123!')

    login_url = reverse('token_obtain_pair')
    resp = api_client.post(login_url, {'username': 'bob', 'password': 'ComplexPass123!'}, format='json')
    assert resp.status_code == status.HTTP_200_OK
    assert 'access' in resp.json()
    assert 'refresh' in resp.json()

    access = resp.json()['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    me_url = reverse('me')
    me_resp = api_client.get(me_url)
    assert me_resp.status_code == status.HTTP_200_OK
    me_data = me_resp.json()
    assert me_data['username'] == 'bob'
    assert me_data['role'] == 'REPORTER'  # default role from Profile


@pytest.mark.django_db
def test_register_password_mismatch_returns_400(api_client):
    url = reverse('register')
    payload = {
        "username": "mismatch",
        "email": "mismatch@example.com",
        "password": "Password1!",
        "password2": "Password2!"
    }
    resp = api_client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    # serializer returns errors; check that password mismatch is reported
    body = resp.json()
    # it can appear under non_field_errors or 'password' - allow either
    assert any(k in body for k in ('password', 'non_field_errors', 'detail', 'errors'))
