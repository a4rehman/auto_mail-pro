"""Pure helpers used by the AutoMail Pro campaign loop."""


def personalize(text, row):
    """Replace {{ColumnName}} placeholders with values from a Google Sheets row."""
    for key, value in row.items():
        placeholder = f"{{{{{key}}}}}"
        text = text.replace(placeholder, str(value))
    return text


def find_email_value(row):
    """Return the first non-empty value in an email column (case-insensitive)."""
    for key, value in row.items():
        if key.strip().lower() == "email":
            return value
    return None