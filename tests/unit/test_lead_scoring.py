from intelligence.lead_scoring import LeadScorer


def test_score():
    scorer = LeadScorer()
    res = scorer.score({'website': 'https://example.com'})
    assert 'lead_score' in res
    assert 'score_breakdown' in res
    assert 0 <= res['lead_score'] <= 100
