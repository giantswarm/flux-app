import logging
from time import sleep
from typing import List

import pykube
import pytest
from pykube.exceptions import HTTPError
from pytest_helm_charts.fixtures import Cluster, NamespaceFactoryFunc, namespace_factory  # noqa: F401
from pytest_helm_charts.giantswarm_app_platform.catalog import CatalogFactoryFunc

# noinspection PyUnresolvedReferences
from fixtures import (  # noqa: F401
    flux_deployments,
    kustomization_factory,
    git_repository_factory,
    helm_repository_factory,
    helm_release_factory
)
from fixtures_helpers import KustomizationFactoryFunc, GitRepositoryFactoryFunc
from helpers import assert_hello_world_is_running

logger = logging.getLogger(__name__)


@pytest.mark.functional
@pytest.mark.upgrade
@pytest.mark.parametrize(
    "test_name", ["simple-app-cr-delivery", "simple-chart-release"]
)
def test_kustomization_works(
        kube_cluster: Cluster,
        flux_deployments: List[pykube.Deployment],  # noqa: F811
        catalog_factory: CatalogFactoryFunc,
        git_repository_factory: GitRepositoryFactoryFunc,  # noqa: F811
        kustomization_factory: KustomizationFactoryFunc,  # noqa: F811
        test_name: str,
) -> None:
    """
    This test checks if it is possible to deploy a Kustomization with GitRepository as a source.
    For upgrade test, the workflow is executed twice, so for both the stable and under-test versions
    a full cycle is executed (app is deployed and then destroyed).
    """
    namespace = "default"
    # TODO: this is a work-around for a problem in the upstream lib (pytest-helm-charts);
    #  fix it there and remove code here
    while True:
        try:
            catalog_factory(
                "giantswarm",
                namespace,
                "https://giantswarm.github.io/giantswarm-catalog/",
            )
            break
        except HTTPError as e:
            if str(e).find("object is being deleted") > -1:
                logger.debug("The catalog is being deleted, need to wait a bit")
                sleep(1)
            else:
                raise
    # end of work-around
    catalog_factory(
        "giantswarm", namespace, "https://giantswarm.github.io/giantswarm-catalog/"
    )

    git_repo_cr_name = "flux-app-tests"
    git_repository_factory(
        git_repo_cr_name,
        namespace,
        "1m",
        "https://github.com/giantswarm/flux-app-tests",
        "feature/init-with-data",
        None,
        "tests/test_cases/**/result",
    )

    kustomization_factory(
        test_name,
        namespace,
        True,
        "1m",
        f"./tests/test_cases/{test_name}",
        git_repo_cr_name,
        "2m",
    )

    assert_hello_world_is_running(kube_cluster.kube_client, "hello-world")
