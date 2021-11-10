from typing import Callable, Optional

from pykube import HTTPClient

from custom_resources import KustomizationCR, GitRepositoryCR
from utils import get_kustomization_obj, wait_for_kustomizations_to_be_ready, get_git_repository_obj, \
    wait_for_git_repositories_to_be_ready

FLUX_CR_READY_TIMEOUT_SEC = 30
KustomizationFactoryFunc = Callable[
    [str, str, bool, str, str, str, str, Optional[str]], KustomizationCR
]

GitRepositoryFactoryFunc = Callable[
    [str, str, str, str, str, Optional[str], Optional[str]], GitRepositoryCR
]


def kustomization_factory_func(
    kube_client: HTTPClient, created_kustomizations: list[KustomizationCR]
) -> KustomizationFactoryFunc:
    """Return a factory object, that can be used to create a new Kustomization CRs"""

    def _kustomization_factory(
        name: str,
        namespace: str,
        prune: bool,
        interval: str,
        repo_path: str,
        git_repository_name: str,
        timeout: str,
        service_account_name: Optional[str] = None,
    ) -> KustomizationCR:
        """A factory function used to create Flux Kustomizations.
        Args:
            name: name of the created Kustomization CR.
            namespace: namespace to create the Kustomization CR in.
            prune: enables garbage collection.
            interval: the interval at which to reconcile the Kustomization.
            repo_path: path to the directory containing the kustomization.yaml file.
            git_repository_name: name of the GitRepository object to get this kustomization from.
            timeout: timeout for apply and health checking operations.
            service_account_name: the name of the Kubernetes service account to impersonate
                when reconciling this Kustomization.
        Returns:
            CatalogCR created or found in the k8s API.
        Raises:
            ValueError: if catalog with the same name, but different URL already exists.
        """
        for k in created_kustomizations:
            if k.metadata["name"] == name and k.metadata["namespace"] == namespace:
                return k

        kustomization = get_kustomization_obj(
            kube_client,
            name,
            namespace,
            prune,
            interval,
            repo_path,
            git_repository_name,
            timeout,
            service_account_name,
        )
        created_kustomizations.append(kustomization)
        kustomization.create()
        wait_for_kustomizations_to_be_ready(
            kube_client, [name], namespace, FLUX_CR_READY_TIMEOUT_SEC, missing_ok=True
        )
        return kustomization

    return _kustomization_factory


def git_repository_factory_func(
        kube_client: HTTPClient, created_git_repositories: list[GitRepositoryCR]
) -> GitRepositoryFactoryFunc:
    """Return a factory object, that can be used to create a new GitRepository CRs"""

    def _git_repository_factory(
            name: str,
            namespace: str,
            interval: str,
            repo_url: str,
            repo_branch: str = "master",
            secret_ref_name: Optional[str] = None,
            ignore_pattern: Optional[str] = None,
    ) -> GitRepositoryCR:
        """A factory function used to create Flux GitRepository.
        Args:
            name: name of the created Kustomization CR.
            namespace: namespace to create the Kustomization CR in.
            interval: the interval at which to check for repository updates.
            repo_url: the repository URL, can be a HTTP/S or SSH address.
            repo_branch: branch of the repo to use.
            secret_ref_name: the secret name containing the Git credentials.
                For HTTPS repositories the secret must contain username and password fields.
                For SSH repositories the secret must contain identity, identity.pub and known_hosts fields.
            ignore_pattern: Ignore overrides the set of excluded patterns in the .sourceignore format
                (which is the same as .gitignore). If not provided, a default will be used,
                consult the documentation for your version to find out what those are.
        Returns:
            CatalogCR created or found in the k8s API.
        Raises:
            ValueError: if catalog with the same name, but different URL already exists.
        """
        for gr in created_git_repositories:
            if gr.metadata["name"] == name and gr.metadata["namespace"] == namespace:
                return gr

        git_repository = get_git_repository_obj(
            kube_client,
            name,
            namespace,
            interval,
            repo_url,
            repo_branch,
            secret_ref_name,
            ignore_pattern
        )
        created_git_repositories.append(git_repository)
        git_repository.create()
        wait_for_git_repositories_to_be_ready(
            kube_client, [name], namespace, FLUX_CR_READY_TIMEOUT_SEC, missing_ok=True
        )
        return git_repository

    return _git_repository_factory
