from typing import Optional


def get_resources(
    resource_type: str,
    namespace: str = "default",
    name: Optional[str] = None,
    label_selector: Optional[str] = None,
) -> dict:
    """List or discover Kubernetes resources from the cluster.

    Use this tool to survey what resources exist in a namespace.
    Supports pods, deployments, services, events, nodes, statefulsets,
    daemonsets, hostedclusters, nodepools, and more.

    Args:
        resource_type: The kind of resource (e.g., "pods", "deployments", "events").
        namespace: Kubernetes namespace to search in.
        name: Optional specific resource name to retrieve.
        label_selector: Optional label filter (e.g., "app=etcd").

    Returns:
        dict: A dictionary with 'status' and either 'items' or 'error_message'.
    """
    ns = namespace.lower()
    rt = resource_type.lower()

    mock_data = {
        "clusters-abc123": {
            "pods": [
                {
                    "name": "etcd-0",
                    "namespace": "clusters-abc123",
                    "status": {"phase": "Running", "containerStatuses": [
                        {"name": "etcd", "ready": False, "restartCount": 14,
                         "state": {"waiting": {"reason": "CrashLoopBackOff",
                                               "message": "back-off 5m0s restarting failed container"}}}
                    ]},
                },
                {
                    "name": "kube-apiserver-7b9f4d6c5-x2k9m",
                    "namespace": "clusters-abc123",
                    "status": {"phase": "Running", "containerStatuses": [
                        {"name": "kube-apiserver", "ready": True, "restartCount": 0,
                         "state": {"running": {"startedAt": "2026-04-28T10:00:00Z"}}}
                    ]},
                },
                {
                    "name": "konnectivity-agent-5f8d7c4b-lm3n",
                    "namespace": "clusters-abc123",
                    "status": {"phase": "Running", "containerStatuses": [
                        {"name": "konnectivity-agent", "ready": True, "restartCount": 0,
                         "state": {"running": {"startedAt": "2026-04-28T10:00:00Z"}}}
                    ]},
                },
            ],
            "deployments": [
                {
                    "name": "kube-apiserver",
                    "namespace": "clusters-abc123",
                    "status": {"replicas": 3, "readyReplicas": 3, "availableReplicas": 3},
                },
            ],
            "events": [
                {
                    "type": "Warning",
                    "reason": "BackOff",
                    "involvedObject": {"kind": "Pod", "name": "etcd-0"},
                    "message": "Back-off restarting failed container etcd in pod etcd-0",
                    "count": 14,
                    "lastTimestamp": "2026-04-29T14:30:00Z",
                },
                {
                    "type": "Warning",
                    "reason": "OOMKilled",
                    "involvedObject": {"kind": "Pod", "name": "etcd-0"},
                    "message": "Container etcd exceeded memory limit",
                    "count": 14,
                    "lastTimestamp": "2026-04-29T14:25:00Z",
                },
            ],
        },
    }

    if ns not in mock_data:
        return {"status": "success", "items": [], "message": f"No resources found in namespace '{namespace}'."}

    ns_data = mock_data[ns]
    if rt not in ns_data:
        return {"status": "success", "items": [], "message": f"No {resource_type} found in namespace '{namespace}'."}

    items = ns_data[rt]

    if name:
        items = [i for i in items if i.get("name") == name]

    if label_selector and "=" in label_selector:
        key, val = label_selector.split("=", 1)
        items = [i for i in items if i.get("labels", {}).get(key) == val]

    return {"status": "success", "items": items, "count": len(items)}
