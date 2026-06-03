from __future__ import annotations

import re
from urllib.parse import urlparse


URL_PATTERN = re.compile(r"\bhttps?://[^\s<>'\"]+|\bwww\.[^\s<>'\"]+", re.IGNORECASE)
IP_PATTERN = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"
)
SHORTENED_DOMAINS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "cutt.ly"}

PATTERN_GROUPS = {
    "urgent_language": [
        r"\burgent\b",
        r"\bimmediately\b",
        r"\bverify now\b",
        r"\baction required\b",
        r"\bsuspended\b",
        r"\blimited time\b",
    ],
    "credential_request": [
        r"\bpassword\b",
        r"\blog[ -]?in\b",
        r"\bverify account\b",
        r"\bcredentials?\b",
        r"\breset your password\b",
    ],
    "financial_language": [
        r"\binvoice\b",
        r"\bpayment\b",
        r"\bbank\b",
        r"\brefund\b",
        r"\bwire transfer\b",
        r"\bcrypto\b",
    ],
    "attachment_mentions": [
        r"\battached\b",
        r"\battachment\b",
        r"\binvoice\.pdf\b",
        r"\bdocument\b",
        r"\bfile\b",
    ],
    "suspicious_sender_hints": [
        r"\breply-to mismatch\b",
        r"\bfrom support\b",
        r"\bsecurity team\b",
        r"\bstrange domain\b",
    ],
    "suspicious_keywords": [
        r"\bclick\b",
        r"\bverify\b",
        r"\baccount\b",
        r"\bupdate\b",
        r"\bsecurity alert\b",
    ],
}


def _clean_url(url: str) -> str:
    return url.rstrip(".,);]")


def _domain_from_url(url: str) -> str:
    parse_target = url if url.lower().startswith(("http://", "https://")) else f"http://{url}"
    parsed = urlparse(parse_target)
    return parsed.netloc.lower().split("@")[-1].split(":")[0]


def _find_pattern_matches(text: str, patterns: list[str]) -> list[str]:
    matches: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            value = match.group(0).strip()
            if value and value not in matches:
                matches.append(value)
    return matches


def extract_indicators(email_text: str, subject: str = "") -> dict[str, object]:
    combined_text = f"{subject or ''} {email_text or ''}".strip()
    urls = []
    for match in URL_PATTERN.finditer(combined_text):
        url = _clean_url(match.group(0))
        if url not in urls:
            urls.append(url)

    domains = []
    for url in urls:
        domain = _domain_from_url(url)
        if domain and domain not in domains:
            domains.append(domain)

    ip_addresses = []
    for match in IP_PATTERN.finditer(combined_text):
        ip_address = match.group(0)
        if ip_address not in ip_addresses:
            ip_addresses.append(ip_address)

    result: dict[str, object] = {
        "urls": urls,
        "domains": domains,
        "ip_addresses": ip_addresses,
        "has_url": bool(urls),
        "has_ip": bool(ip_addresses),
        "shortened_url_hints": [
            domain for domain in domains if domain in SHORTENED_DOMAINS
        ],
    }

    for key, patterns in PATTERN_GROUPS.items():
        result[key] = _find_pattern_matches(combined_text, patterns)

    return result
