from typing import Callable, Optional

from pykube import HTTPClient

from custom_resources import KustomizationCR
from utils import get_kustomization_obj, wait_for_kustomizations_to_be_ready

FLUX_CR_READY_TIMEOUT_SEC = 30
KustomizationFactoryFunc = Callable[
    [str, str, bool, str, str, str, str, Optional[str]], KustomizationCR
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
            name: name of the created Catalog CR. If the Catalog with this name already exists
                in the namespace but the URL is different, it's an error. If the URL and name
                are the same, nothing is done.
            namespace: namespace to create the Catalog CR in.
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
