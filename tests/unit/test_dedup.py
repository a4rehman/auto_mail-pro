from database.repository import lead_hash, _normalize_domain


def test_normalize_domain():
    assert _normalize_domain('https://www.example.com') == 'example.com'
    assert _normalize_domain('http://example.com') == 'example.com'


def test_lead_hash():
    h1 = lead_hash({'google_place_id': '123'})
    h2 = lead_hash({'google_place_id': '123'})
    assert h1 == h2
