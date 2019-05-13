import pytest


@pytest.mark.django_db
def test_admin_smoke(admin_client):
    assert admin_client.get('/admin/lippukala/code/').status_code == 200
    assert admin_client.get('/admin/lippukala/order/').status_code == 200
