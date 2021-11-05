from typing import Optional

from pykube import HTTPClient

from custom_resources import GitRepositoryCR, KustomizationCR


def get_git_repository_obj(kube_client: HTTPClient, name: str, namespace: str, interval: str, repo_url: str,
                           repo_branch: str = "master",
                           secret_ref_name: Optional[str] = None,
                           ignore_pattern: Optional[str] = None,
                           ) -> GitRepositoryCR:
    cr = {
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
        }
    }
    if secret_ref_name:
        cr["spec"]["secretRef"] = {
            "name": secret_ref_name,
        }
    if ignore_pattern:
        cr["spec"]["ignore"] = ignore_pattern
    return GitRepositoryCR(kube_client, cr)


def get_kustomize_obj(kube_client: HTTPClient, name: str, namespace: str, service_account_name: str,
                      prune: bool, interval: str, repo_path: str, git_repository_name: str,
                      timeout: str
                      ) -> KustomizationCR:
    cr = {
        "metadata": {
            "name": name,
            "namespace": namespace,
        },
        "spec": {
            "serviceAccountName": service_account_name,
            "prune": prune,
            "interval": interval,
            "path": repo_path,
            "sourceRef": {
                "kind": "GitRepository",
                "name": git_repository_name,
            },
            "timeout": timeout
        }
    }
    return KustomizationCR(kube_client, cr)
