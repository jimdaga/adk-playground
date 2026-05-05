from typing import Optional


def query_history(
    cluster_id: Optional[str] = None,
    namespace: Optional[str] = None,
    days: int = 7,
) -> dict:
    """Query the diagnostic data lake for historical findings.

    Searches past diagnostic findings for patterns, recurring issues,
    and prior root causes related to a cluster or namespace.

    Args:
        cluster_id: Filter by cluster ID (optional).
        namespace: Filter by namespace (optional).
        days: Look back this many days (default 7).

    Returns:
        dict: A dictionary with 'status' and 'findings' list.
    """
    mock_findings = [
        {
            "timestamp": "2026-04-27T08:30:00Z",
            "cluster_id": "abc123",
            "namespace": "clusters-abc123",
            "severity": "critical",
            "root_cause": "etcd OOMKilled due to database size exceeding memory limit during compaction",
            "confidence": "high",
            "recommendation": "Increase etcd memory limit to 1Gi and schedule defragmentation",
            "status": "success",
        },
        {
            "timestamp": "2026-04-24T16:00:00Z",
            "cluster_id": "abc123",
            "namespace": "clusters-abc123",
            "severity": "warning",
            "root_cause": "etcd database size at 85% of quota, compaction delayed",
            "confidence": "medium",
            "recommendation": "Monitor database growth and ensure defrag sidecar is running",
            "status": "success",
        },
        {
            "timestamp": "2026-04-20T12:15:00Z",
            "cluster_id": "def456",
            "namespace": "clusters-def456",
            "severity": "warning",
            "root_cause": "NodePool scaling blocked by insufficient quota in us-central1",
            "confidence": "high",
            "recommendation": "Request quota increase for n2-standard-4 in us-central1",
            "status": "success",
        },
    ]

    results = mock_findings

    if cluster_id:
        results = [f for f in results if f.get("cluster_id") == cluster_id]
    if namespace:
        results = [f for f in results if f.get("namespace") == namespace]

    return {
        "status": "success",
        "findings": results,
        "count": len(results),
        "query": {"cluster_id": cluster_id, "namespace": namespace, "days": days},
    }
