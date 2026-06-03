from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Any

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline import analyze_email  # noqa: E402


SAMPLE_CATALOG = {
    "benign_01": {
        "type": "benign",
        "label": "Team planning reminder",
        "subject": "Team lunch update",
        "path": PROJECT_ROOT / "data" / "samples" / "benign_email.txt",
    },
    "benign_02": {
        "type": "benign",
        "label": "IT maintenance notice",
        "subject": "Scheduled VPN maintenance",
        "path": PROJECT_ROOT / "data" / "samples" / "benign_02_it_maintenance.txt",
    },
    "benign_03": {
        "type": "benign",
        "label": "HR policy update",
        "subject": "Updated holiday policy",
        "path": PROJECT_ROOT / "data" / "samples" / "benign_03_hr_policy.txt",
    },
    "benign_04": {
        "type": "benign",
        "label": "Invoice clarification",
        "subject": "Invoice correction from finance",
        "path": PROJECT_ROOT / "data" / "samples" / "benign_04_invoice_clarification.txt",
    },
    "benign_05": {
        "type": "benign",
        "label": "Security awareness",
        "subject": "Security awareness training recap",
        "path": PROJECT_ROOT / "data" / "samples" / "benign_05_security_awareness.txt",
    },
    "benign_06": {
        "type": "benign",
        "label": "Support ticket update",
        "subject": "Support ticket resolved",
        "path": PROJECT_ROOT / "data" / "samples" / "benign_06_support_ticket.txt",
    },
    "benign_07": {
        "type": "benign",
        "label": "Vendor newsletter",
        "subject": "Quarterly vendor newsletter",
        "path": PROJECT_ROOT / "data" / "samples" / "benign_07_vendor_newsletter.txt",
    },
    "benign_08": {
        "type": "benign",
        "label": "Calendar invite",
        "subject": "Calendar invite: design review",
        "path": PROJECT_ROOT / "data" / "samples" / "benign_08_calendar_invite.txt",
    },
    "benign_09": {
        "type": "benign",
        "label": "Password policy notice",
        "subject": "Password policy reminder",
        "path": PROJECT_ROOT / "data" / "samples" / "benign_09_password_policy.txt",
    },
    "benign_10": {
        "type": "benign",
        "label": "Internal audit request",
        "subject": "Internal audit evidence request",
        "path": PROJECT_ROOT / "data" / "samples" / "benign_10_internal_audit.txt",
    },
    "phishing_01": {
        "type": "phishing",
        "label": "Credential reset lure",
        "subject": "Action required",
        "path": PROJECT_ROOT / "data" / "samples" / "phishing_email.txt",
    },
    "phishing_02": {
        "type": "phishing",
        "label": "Fake invoice link",
        "subject": "Urgent invoice payment required",
        "path": PROJECT_ROOT / "data" / "samples" / "phishing_02_fake_invoice.txt",
    },
    "phishing_03": {
        "type": "phishing",
        "label": "Attachment lure",
        "subject": "Document shared with you",
        "path": PROJECT_ROOT / "data" / "samples" / "phishing_03_attachment_lure.txt",
    },
    "phishing_04": {
        "type": "phishing",
        "label": "Shortened URL",
        "subject": "Security alert: verify now",
        "path": PROJECT_ROOT / "data" / "samples" / "phishing_04_shortened_url.txt",
    },
    "phishing_05": {
        "type": "phishing",
        "label": "IP address link",
        "subject": "Mailbox access warning",
        "path": PROJECT_ROOT / "data" / "samples" / "phishing_05_ip_address.txt",
    },
    "phishing_06": {
        "type": "phishing",
        "label": "Bank refund lure",
        "subject": "Refund pending confirmation",
        "path": PROJECT_ROOT / "data" / "samples" / "phishing_06_bank_refund.txt",
    },
    "phishing_07": {
        "type": "phishing",
        "label": "Cloud storage spoof",
        "subject": "Shared file expires today",
        "path": PROJECT_ROOT / "data" / "samples" / "phishing_07_cloud_storage.txt",
    },
    "phishing_08": {
        "type": "phishing",
        "label": "Crypto wallet lure",
        "subject": "Crypto wallet verification",
        "path": PROJECT_ROOT / "data" / "samples" / "phishing_08_crypto_wallet.txt",
    },
    "phishing_09": {
        "type": "phishing",
        "label": "Executive gift card",
        "subject": "Quick favor before meeting",
        "path": PROJECT_ROOT / "data" / "samples" / "phishing_09_gift_card.txt",
    },
    "phishing_10": {
        "type": "phishing",
        "label": "MFA fatigue lure",
        "subject": "MFA push verification failed",
        "path": PROJECT_ROOT / "data" / "samples" / "phishing_10_mfa_fatigue.txt",
    },
}
DEFAULT_AUDIT_LOG = PROJECT_ROOT / "logs" / "audit_log.csv"
SAFE_AUDIT_COLUMNS = [
    "timestamp_utc",
    "email_hash",
    "prediction",
    "phishing_probability",
    "risk_score",
    "risk_level",
    "mitre_technique_ids",
]
INDICATOR_FIELDS = [
    ("urls", "URLs"),
    ("domains", "Domains"),
    ("ip_addresses", "IP addresses"),
    ("urgent_language", "Urgent language"),
    ("credential_request", "Credential requests"),
    ("financial_language", "Financial language"),
    ("attachment_mentions", "Attachment mentions"),
    ("suspicious_keywords", "Suspicious keywords"),
    ("shortened_url_hints", "Shortened URL hints"),
]


def load_sample_email(sample_name: str) -> str:
    sample = SAMPLE_CATALOG.get(sample_name)
    if sample is None:
        raise ValueError(f"Unknown sample: {sample_name}")
    sample_path = sample["path"]
    return sample_path.read_text(encoding="utf-8").strip()


def sample_payload(sample_name: str) -> dict[str, str]:
    sample = SAMPLE_CATALOG.get(sample_name)
    if sample is None:
        raise ValueError(f"Unknown sample: {sample_name}")
    return {
        "label": str(sample["label"]),
        "subject": str(sample["subject"]),
        "email_body": load_sample_email(sample_name),
    }


def sample_options(sample_type: str) -> list[dict[str, str]]:
    return [
        {
            "key": key,
            "label": str(sample["label"]),
            "subject": str(sample["subject"]),
        }
        for key, sample in SAMPLE_CATALOG.items()
        if sample["type"] == sample_type
    ]


def read_audit_preview(
    log_path: str | Path = DEFAULT_AUDIT_LOG,
    row_limit: int = 10,
) -> list[dict[str, str]]:
    path = Path(log_path)
    if not path.exists():
        return []

    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    preview_rows = rows[-row_limit:]
    return [
        {column: row.get(column, "") for column in SAFE_AUDIT_COLUMNS}
        for row in preview_rows
    ]


def _format_probability(value: Any) -> str:
    try:
        return f"{float(value):.1%}"
    except (TypeError, ValueError):
        return "N/A"


def _format_score(value: Any) -> str:
    try:
        return str(int(value))
    except (TypeError, ValueError):
        return "N/A"


def _indicator_table(indicators: dict[str, Any]) -> list[dict[str, str]]:
    rows = []
    for key, label in INDICATOR_FIELDS:
        value = indicators.get(key, [])
        if isinstance(value, list):
            display_value = ", ".join(str(item) for item in value) if value else "None"
            count = len(value)
        else:
            display_value = str(value)
            count = int(bool(value))
        rows.append({"Indicator": label, "Count": str(count), "Evidence": display_value})
    return rows


def _mitre_table(mitre_mappings: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = []
    for mapping in mitre_mappings:
        evidence = mapping.get("evidence", [])
        if isinstance(evidence, list):
            evidence_text = "; ".join(str(item) for item in evidence)
        else:
            evidence_text = str(evidence)
        rows.append(
            {
                "technique_id": str(mapping.get("technique_id", "")),
                "technique_name": str(mapping.get("technique_name", "")),
                "tactic": str(mapping.get("tactic", "")),
                "evidence": evidence_text,
            }
        )
    return rows


def _ensure_state_defaults() -> None:
    st.session_state.setdefault("subject", "")
    st.session_state.setdefault("email_body", "")
    st.session_state.setdefault("analysis_result", None)


def _render_project_summary() -> None:
    st.markdown(
        """
        Local phishing analysis for SOC-style email triage. The assistant uses rule-based
        indicator extraction, MITRE ATT&CK mapping, risk scoring, safe audit logging, and
        a trained local baseline model. No external API or API key is required. Full email
        bodies are not stored in audit logs.
        """
    )


def _render_sample_loader() -> None:
    st.markdown("**Load a safe demo sample**")
    benign_col, phishing_col = st.columns(2)
    benign_options = sample_options("benign")
    phishing_options = sample_options("phishing")

    selected_benign = benign_col.selectbox(
        "Benign sample",
        options=[option["key"] for option in benign_options],
        format_func=lambda key: SAMPLE_CATALOG[key]["label"],
        key="selected_benign_sample",
    )
    benign_col.button(
        "Load selected benign sample",
        on_click=_load_sample_into_state,
        args=(selected_benign,),
        width="stretch",
    )
    selected_phishing = phishing_col.selectbox(
        "Phishing sample",
        options=[option["key"] for option in phishing_options],
        format_func=lambda key: SAMPLE_CATALOG[key]["label"],
        key="selected_phishing_sample",
    )
    phishing_col.button(
        "Load selected phishing sample",
        on_click=_load_sample_into_state,
        args=(selected_phishing,),
        width="stretch",
    )


def _load_sample_into_state(sample_name: str) -> None:
    payload = sample_payload(sample_name)
    st.session_state["subject"] = payload["subject"]
    st.session_state["email_body"] = payload["email_body"]
    st.session_state["analysis_result"] = None


def _render_analysis_result(result: dict[str, Any]) -> None:
    prediction = result.get("prediction", {})
    risk = result.get("risk", {})
    indicators = result.get("indicators", {})
    mitre_mappings = result.get("mitre_mappings", [])

    st.subheader("Analysis Summary")
    prediction_col, probability_col, confidence_col, risk_col = st.columns(4)
    prediction_col.metric("Prediction", str(prediction.get("prediction", "Unknown")))
    probability_col.metric(
        "Phishing probability",
        _format_probability(prediction.get("phishing_probability")),
    )
    confidence_col.metric("Confidence", _format_probability(prediction.get("confidence")))
    risk_col.metric(
        "Risk",
        f"{risk.get('risk_level', 'Unknown')} ({_format_score(risk.get('risk_score'))}/100)",
    )

    risk_factors = risk.get("risk_factors", [])
    if risk_factors:
        st.markdown("**Risk factors**")
        for factor in risk_factors:
            st.markdown(f"- {factor}")

    with st.expander("Extracted Indicators", expanded=True):
        st.dataframe(_indicator_table(indicators), width="stretch", hide_index=True)

    st.subheader("MITRE ATT&CK Mapping")
    mitre_rows = _mitre_table(mitre_mappings)
    if mitre_rows:
        st.dataframe(mitre_rows, width="stretch", hide_index=True)
    else:
        st.info("No MITRE techniques were mapped from the available evidence.")

    st.subheader("Explanation")
    st.write(result.get("explanation", "No explanation returned."))

    st.subheader("Recommendations")
    for recommendation in result.get("recommendations", []):
        st.markdown(f"- {recommendation}")

    audit_logged = result.get("audit_logged", False)
    if audit_logged:
        st.success("Audit log updated. Full email bodies are not stored.")
    else:
        st.info("Audit logging was not performed for this analysis.")


def _render_audit_preview() -> None:
    st.subheader("Audit Log Preview")
    st.caption("Showing safe metadata only. Full email bodies are not displayed or stored.")
    preview_rows = read_audit_preview(DEFAULT_AUDIT_LOG, row_limit=10)
    if preview_rows:
        st.dataframe(preview_rows, width="stretch", hide_index=True)
    else:
        st.info("No audit log rows found yet.")


def main() -> None:
    st.set_page_config(
        page_title="AI-Based Phishing Detection SOC Assistant",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    _ensure_state_defaults()

    st.title("AI-Based Phishing Detection and Risk Assessment SOC Assistant")
    _render_project_summary()

    st.subheader("Email Input")
    _render_sample_loader()
    subject = st.text_input("Subject", key="subject")
    email_body = st.text_area("Email body", key="email_body", height=240)

    if st.button("Analyze", type="primary"):
        if not subject.strip() and not email_body.strip():
            st.warning("Enter a subject, an email body, or load a sample before analyzing.")
        else:
            try:
                st.session_state["analysis_result"] = analyze_email(
                    email_text=email_body,
                    subject=subject,
                    log=True,
                )
            except FileNotFoundError as error:
                st.error(str(error))
                st.code(".venv/bin/python -m src.train_baseline", language="bash")

    result = st.session_state.get("analysis_result")
    if result:
        _render_analysis_result(result)

    _render_audit_preview()


if __name__ == "__main__":
    main()
