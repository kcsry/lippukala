from lippukala.models import Code

from .utils import create_test_order


def test_pos_view(admin_client, adapter):
    for x in range(5):
        create_test_order(adapter)
    admin_client.get("/pos/")
    codes = admin_client.get("/pos/", {"json": "1"}).json()["codes"]
    code_id = codes[0]["id"]
    admin_client.post("/pos/", {"use": code_id, "station": "hurp"})
    code = Code.objects.get(pk=code_id)
    assert code.is_used
    assert code.used_at == "hurp"
