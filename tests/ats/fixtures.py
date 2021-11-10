from typing import Iterable, TypeVar, Callable

import pykube
import pytest
from pytest_helm_charts.clusters import Cluster
from pytest_helm_charts.utils import wait_for_deployments_to_run

from custom_resources import NamespacedFluxCR
from fixtures_helpers import KustomizationFactoryFunc, kustomization_factory_func

FLUX_NAMESPACE_NAME = "default"
FLUX_DEPLOYMENT_TIMEOUT: int = 180


# scope "module" means this is run only once, for the first test case requesting! It might be tricky
# if you want to assert this multiple times
@pytest.fixture(scope="module")
def flux_deployments(kube_cluster: Cluster) -> list[pykube.Deployment]:
    deployments = wait_for_deployments_to_run(
        kube_cluster.kube_client,
        [
            "helm-controller",
            "image-automation-controller",
            "image-reflector-controller",
            "kustomize-controller",
            "notification-controller",
            "source-controller",
        ],
        FLUX_NAMESPACE_NAME,
        FLUX_DEPLOYMENT_TIMEOUT,
    )
    return deployments


T = TypeVar("T", bound=NamespacedFluxCR)
FactoryFunc = Callable[..., T]
MetaFactoryFunc = Callable[[pykube.HTTPClient, list[T]], FactoryFunc]


def _flux_factory(
    kube_cluster: Cluster, meta_func: MetaFactoryFunc
) -> Iterable[FactoryFunc]:
    created_objects: list[NamespacedFluxCR] = []

    yield meta_func(kube_cluster.kube_client, created_objects)

    for flux_object in created_objects:
        flux_object.delete()


@pytest.fixture(scope="module")
def kustomization_factory(kube_cluster: Cluster) -> Iterable[KustomizationFactoryFunc]:
    return _flux_factory(kube_cluster, kustomization_factory_func)
