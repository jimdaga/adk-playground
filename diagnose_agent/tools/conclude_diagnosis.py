from typing import List


def conclude_diagnosis(
    root_cause: str,
    confidence: str,
    evidence: List[str],
    recommendation: str,
    severity: str,
) -> dict:
    """Signal that the investigation is complete with a structured diagnosis.

    Call this tool ONLY when you have gathered sufficient evidence to
    provide a specific, actionable diagnosis. Do not call it with vague
    conclusions like 'unknown' or 'needs further investigation'.

    Args:
        root_cause: Specific description of the root cause, grounded in evidence.
        confidence: Confidence level — one of 'high', 'medium', 'low'.
        evidence: List of specific findings that support the root cause.
        recommendation: Actionable steps to resolve the issue.
        severity: Issue severity — one of 'critical', 'warning', 'info'.

    Returns:
        dict: The structured diagnosis finding.
    """
    return {
        "status": "success",
        "diagnosis": {
            "root_cause": root_cause,
            "confidence": confidence,
            "evidence": evidence,
            "recommendation": recommendation,
            "severity": severity,
        },
    }
