import logging
from typing import List

import pykube
import pytest

from pytest_helm_charts.k8s.fixtures import NamespaceFactoryFunc
from pytest_helm_charts.clusters import Cluster
from pytest_helm_charts.flux.helm_release import (
    HelmReleaseFactoryFunc,
    ChartTemplate,
    CrossNamespaceObjectReference,
)
from pytest_helm_charts.flux.helm_repository import HelmRepositoryFactoryFunc

from helpers import assert_hello_world_is_running

logger = logging.getLogger(__name__)

APP_DEPLOYMENT_TIMEOUT_SEC = 180


@pytest.mark.functional
@pytest.mark.upgrade
def test_helm_release_works(
    kube_cluster: Cluster,
    flux_deployments: List[pykube.Deployment],
    namespace_factory: NamespaceFactoryFunc,
    helm_repository_factory: HelmRepositoryFactoryFunc,
    helm_release_factory: HelmReleaseFactoryFunc,
) -> None:
    """
    This test checks if it is possible to deploy a HelmRelease with HelmRepository as a source.
    For upgrade test, the workflow is executed twice, so for both the stable and under-test versions
    a full cycle is executed (app is deployed and then destroyed).
    """
    namespace = "hello-world"
    app_namespace = "hello-world"
    namespace_factory(app_namespace)

    helm_registry_name = "giantswarm"
    helm_repository_factory(
        helm_registry_name,
        namespace,
        "1m",
        "https://giantswarm.github.io/giantswarm-catalog",
    )
    helm_release_factory(
        "hello-world",
        app_namespace,
        chart=ChartTemplate(
            chart="hello-world",
            version="2.3.0",
            sourceRef=CrossNamespaceObjectReference(
                kind="HelmRepository",
                name=helm_registry_name,
                namespace=namespace,
            ),
        ),
        interval="1m",
    )

    assert_hello_world_is_running(kube_cluster.kube_client, app_namespace)
