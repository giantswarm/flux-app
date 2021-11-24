import logging
from typing import Optional, Any

from pykube import HTTPClient
from pytest_helm_charts.utils import wait_for_namespaced_objects_condition

from custom_resources import GitRepositoryCR, KustomizationCR, NamespacedFluxCR

logger = logging.getLogger(__name__)


def get_git_repository_obj(
    kube_client: HTTPClient,
    name: str,
    namespace: str,
    interval: str,
    repo_url: str,
    repo_branch: str = "master",
    secret_ref_name: Optional[str] = None,
    ignore_pattern: Optional[str] = None,
) -> GitRepositoryCR:
    cr: dict[str, Any] = {
        "apiVersion": GitRepositoryCR.version,
        "kind": GitRepositoryCR.kind,
        "metadata": {
            "name": name,
            "namespace": namespace,
        },
        "spec": {
            "interval": interval,
            "url": repo_url,
            "ref": {
                "branch": repo_branch,
            },
        },
    }
    if secret_ref_name:
        cr["spec"]["secretRef"] = {
            "name": secret_ref_name,
        }
    if ignore_pattern:
        cr["spec"]["ignore"] = ignore_pattern
    return GitRepositoryCR(kube_client, cr)


def get_kustomization_obj(
    kube_client: HTTPClient,
    name: str,
    namespace: str,
    prune: bool,
    interval: str,
    repo_path: str,
    git_repository_name: str,
    timeout: str,
    service_account_name: Optional[str] = None,
) -> KustomizationCR:
    cr: dict[str, Any] = {
        "apiVersion": KustomizationCR.version,
        "kind": KustomizationCR.kind,
        "metadata": {
            "name": name,
            "namespace": namespace,
        },
        "spec": {
            "prune": prune,
            "interval": interval,
            "path": repo_path,
            "sourceRef": {
                "kind": "GitRepository",
                "name": git_repository_name,
            },
            "timeout": timeout,
        },
    }
    if service_account_name:
        cr["spec"]["serviceAccountName"] = service_account_name
    return KustomizationCR(kube_client, cr)


def _flux_cr_ready(flux_obj: NamespacedFluxCR) -> bool:
    has_conditions = "status" in flux_obj.obj and "conditions" in flux_obj.obj["status"]
    if not has_conditions:
        return False
    conditions_count = len(flux_obj.obj["status"]["conditions"])
    if conditions_count == 0:
        return False
    if conditions_count > 1:
        logging.warning(
            f"Found '{conditions_count}' status conditions when expecting just 1. Using only"
            f" the first one on the list."
        )
    condition = flux_obj.obj["status"]["conditions"][0]
    return condition["type"] == "Ready" and condition["status"] == "True"


def wait_for_git_repositories_to_be_ready(
    kube_client: HTTPClient,
    git_repo_names: list[str],
    git_repo_namespace: str,
    timeout_sec: int,
    missing_ok: bool = False,
) -> list[GitRepositoryCR]:
    git_repos = wait_for_namespaced_objects_condition(
        kube_client,
        GitRepositoryCR,
        git_repo_names,
        git_repo_namespace,
        _flux_cr_ready,
        timeout_sec,
        missing_ok,
    )
    return git_repos


def wait_for_kustomizations_to_be_ready(
    kube_client: HTTPClient,
    kustomization_names: list[str],
    kustomization_namespace: str,
    timeout_sec: int,
    missing_ok: bool = False,
) -> list[KustomizationCR]:
    kustomizations = wait_for_namespaced_objects_condition(
        kube_client,
        KustomizationCR,
        kustomization_names,
        kustomization_namespace,
        _flux_cr_ready,
        timeout_sec,
        missing_ok,
    )
    return kustomizations
