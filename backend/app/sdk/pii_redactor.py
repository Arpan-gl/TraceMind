import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}")
CARD_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def redact(text: str) -> str:
    redacted = EMAIL_RE.sub("[EMAIL]", text)
    redacted = PHONE_RE.sub("[PHONE]", redacted)
    redacted = CARD_RE.sub("[CARD]", redacted)
    redacted = SSN_RE.sub("[SSN]", redacted)
    return redacted
