from typing import Optional


def get_logs(
    namespace: str,
    pod: str,
    container: Optional[str] = None,
    tail_lines: int = 100,
    previous: bool = False,
    since_seconds: Optional[int] = None,
) -> dict:
    """Retrieve container logs from a specific pod.

    Use this to examine application output, error messages, and crash traces.
    Set previous=True to get logs from the last crashed container instance.

    Args:
        namespace: Kubernetes namespace.
        pod: Pod name.
        container: Specific container name (optional if pod has one container).
        tail_lines: Number of lines from the end (default 100, max 1000).
        previous: If True, return logs from the previously terminated container.
        since_seconds: Only return logs newer than this many seconds.

    Returns:
        dict: A dictionary with 'status' and either 'logs' or 'error_message'.
    """
    key = f"{namespace}/{pod}"

    current_logs = {
        "clusters-abc123/etcd-0": (
            "2026-04-29T14:20:00Z etcd: starting etcd server\n"
            "2026-04-29T14:20:01Z etcd: loading snapshot from /var/lib/etcd/member/snap/db\n"
            "2026-04-29T14:20:02Z etcd: database size: 498MB\n"
            "2026-04-29T14:20:03Z etcd: applying WAL entries\n"
            "2026-04-29T14:20:15Z etcd: WARNING: database size 498MB approaching quota 512MB\n"
            "2026-04-29T14:20:30Z etcd: compaction triggered\n"
            "2026-04-29T14:21:00Z etcd: memory usage exceeded limit during compaction\n"
            "2026-04-29T14:21:01Z etcd: received signal: killed\n"
        ),
    }

    previous_logs = {
        "clusters-abc123/etcd-0": (
            "2026-04-29T14:15:00Z etcd: starting etcd server\n"
            "2026-04-29T14:15:01Z etcd: loading snapshot from /var/lib/etcd/member/snap/db\n"
            "2026-04-29T14:15:02Z etcd: database size: 497MB\n"
            "2026-04-29T14:15:10Z etcd: WARNING: database size 497MB approaching quota 512MB\n"
            "2026-04-29T14:15:45Z etcd: compaction triggered\n"
            "2026-04-29T14:16:30Z etcd: memory usage exceeded limit during compaction\n"
            "2026-04-29T14:16:31Z fatal error: runtime: out of memory\n"
            "2026-04-29T14:16:31Z goroutine 1 [running]:\n"
            "2026-04-29T14:16:31Z runtime.throw({0x1a2b3c4, 0x10})\n"
        ),
    }

    log_source = previous_logs if previous else current_logs

    if key not in log_source:
        return {
            "status": "error",
            "error_message": f"No {'previous ' if previous else ''}logs found for pod '{pod}' in namespace '{namespace}'.",
        }

    lines = log_source[key].strip().split("\n")
    lines = lines[-min(tail_lines, len(lines)):]

    return {"status": "success", "logs": "\n".join(lines), "line_count": len(lines)}
