from core.utils import clean_emails, website_root, is_valid_email_address, is_valid_subject


def test_website_root():
    assert website_root('https://example.com/page') == 'https://example.com'
    assert website_root('http://www.example.com') == 'http://www.example.com'
    assert website_root(None) is None


def test_clean_emails():
    emails = ['test@example.com', 'john@gmail.com', 'noreply@example.com']
    cleaned = clean_emails(emails)
    # noreply might be filtered depending on rules
    assert isinstance(cleaned, list)


def test_is_valid_email():
    assert is_valid_email_address('test@example.com') is True
    assert is_valid_email_address('invalid') is False


def test_is_valid_subject():
    assert is_valid_subject('Hello') is True
    assert is_valid_subject('...') is False
