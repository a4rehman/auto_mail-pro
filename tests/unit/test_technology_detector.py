from enrichment.technology_detector import detect_technologies


def test_detect_tech():
    html = '<html><head><script src="https://www.googletagmanager.com/gtm.js"></script></head><body></body></html>'
    tech = detect_technologies(html)
    assert isinstance(tech, list)
