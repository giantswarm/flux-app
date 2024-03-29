import logging
import time
from typing import List

import pykube
import pytest
from pytest_helm_charts.k8s.fixtures import NamespaceFactoryFunc
from pytest_helm_charts.clusters import Cluster
from pytest_helm_charts.flux.git_repository import GitRepositoryFactoryFunc
from pytest_helm_charts.flux.kustomization import KustomizationFactoryFunc
from pytest_helm_charts.giantswarm_app_platform.catalog import CatalogFactoryFunc

from helpers import assert_hello_world_is_running

logger = logging.getLogger(__name__)


@pytest.mark.functional
# @pytest.mark.upgrade
@pytest.mark.parametrize(
    "test_name", ["simple-app-cr-delivery", "simple-chart-release"]
)
def test_kustomization_works(
    kube_cluster: Cluster,
    flux_deployments: List[pykube.Deployment],
    catalog_factory: CatalogFactoryFunc,
    git_repository_factory: GitRepositoryFactoryFunc,
    kustomization_factory_function_scope: KustomizationFactoryFunc,
    namespace_factory: NamespaceFactoryFunc,
    test_name: str,
) -> None:
    """
    This test checks if it is possible to deploy a Kustomization with GitRepository as a source.
    For upgrade test, the workflow is executed twice, so for both the stable and under-test versions
    a full cycle is executed (app is deployed and then destroyed).
    """
    namespace = "default"
    catalog_factory(
        "giantswarm", namespace, "https://giantswarm.github.io/giantswarm-catalog/"
    )

    git_repo_cr_name = "flux-app-tests"
    git_repository_factory(
        git_repo_cr_name,
        namespace,
        "1m",
        "https://github.com/giantswarm/flux-app-tests",
        "main",
        ignore_pattern="tests/test_cases/**/result",
    )

    kustomization_factory_function_scope(
        test_name,
        namespace,
        True,
        "1m",
        f"./tests/test_cases/{test_name}",
        git_repo_cr_name,
        "2m",
    )

    time.sleep(1800)

    assert_hello_world_is_running(kube_cluster.kube_client, "hello-world")
