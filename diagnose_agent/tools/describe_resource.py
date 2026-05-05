def describe_resource(resource_type: str, namespace: str, name: str) -> dict:
    """Get detailed information about a specific Kubernetes resource.

    Returns the full spec, status, conditions, and related events
    for the named resource. Use this after discovery to investigate
    a specific resource in depth.

    Args:
        resource_type: The kind of resource (e.g., "pods", "deployments").
        namespace: Kubernetes namespace.
        name: Exact resource name.

    Returns:
        dict: A dictionary with 'status' and either 'resource' or 'error_message'.
    """
    rt = resource_type.lower()
    key = f"{namespace}/{rt}/{name}"

    mock_descriptions = {
        "clusters-abc123/pods/etcd-0": {
            "kind": "Pod",
            "metadata": {"name": "etcd-0", "namespace": "clusters-abc123",
                         "labels": {"app": "etcd", "statefulset": "etcd"}},
            "spec": {
                "containers": [{
                    "name": "etcd",
                    "image": "quay.io/openshift/etcd:v3.5.12",
                    "resources": {"limits": {"memory": "512Mi"}, "requests": {"memory": "256Mi"}},
                }],
            },
            "status": {
                "phase": "Running",
                "conditions": [
                    {"type": "Ready", "status": "False", "reason": "ContainersNotReady",
                     "message": "containers with unready status: [etcd]",
                     "lastTransitionTime": "2026-04-29T14:25:00Z"},
                    {"type": "ContainersReady", "status": "False", "reason": "ContainersNotReady",
                     "lastTransitionTime": "2026-04-29T14:25:00Z"},
                ],
                "containerStatuses": [{
                    "name": "etcd",
                    "ready": False,
                    "restartCount": 14,
                    "state": {"waiting": {"reason": "CrashLoopBackOff",
                                          "message": "back-off 5m0s restarting failed container"}},
                    "lastState": {"terminated": {"exitCode": 137, "reason": "OOMKilled",
                                                 "finishedAt": "2026-04-29T14:24:55Z"}},
                }],
                "startTime": "2026-04-28T10:00:00Z",
            },
        },
        "clusters-abc123/pods/kube-apiserver-7b9f4d6c5-x2k9m": {
            "kind": "Pod",
            "metadata": {"name": "kube-apiserver-7b9f4d6c5-x2k9m", "namespace": "clusters-abc123"},
            "status": {
                "phase": "Running",
                "conditions": [
                    {"type": "Ready", "status": "True", "lastTransitionTime": "2026-04-28T10:01:00Z"},
                ],
                "containerStatuses": [{
                    "name": "kube-apiserver", "ready": True, "restartCount": 0,
                    "state": {"running": {"startedAt": "2026-04-28T10:00:30Z"}},
                }],
            },
        },
    }

    if key not in mock_descriptions:
        return {
            "status": "error",
            "error_message": f"Resource '{name}' of type '{resource_type}' not found in namespace '{namespace}'.",
        }

    return {"status": "success", "resource": mock_descriptions[key]}
