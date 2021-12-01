import logging
from time import sleep
from typing import List

import pykube
import pytest
from pykube.exceptions import HTTPError
from pytest_helm_charts.fixtures import Cluster
from pytest_helm_charts.giantswarm_app_platform.catalog import CatalogFactoryFunc
from pytest_helm_charts.utils import wait_for_deployments_to_run

# noinspection PyUnresolvedReferences
from fixtures import (  # noqa: F401
    flux_deployments,
    kustomization_factory,
    git_repository_factory,
)
from fixtures_helpers import KustomizationFactoryFunc, GitRepositoryFactoryFunc, HelmReleaseFactoryFunc, \
    HelmRepositoryFactoryFunc

logger = logging.getLogger(__name__)

APP_DEPLOYMENT_TIMEOUT_SEC = 180


@pytest.mark.smoke
def test_api_working(kube_cluster: Cluster) -> None:
    """Very minimalistic example of using the [kube_cluster](pytest_helm_charts.fixtures.kube_cluster)
    fixture to get an instance of [Cluster](pytest_helm_charts.clusters.Cluster) under test
    and access its [kube_client](pytest_helm_charts.clusters.Cluster.kube_client) property
    to get access to Kubernetes API of cluster under test.
    Please refer to [pykube](https://pykube.readthedocs.io/en/latest/api/pykube.html) to get docs
    for [HTTPClient](https://pykube.readthedocs.io/en/latest/api/pykube.html#pykube.http.HTTPClient).
    """
    assert kube_cluster.kube_client is not None
    assert len(pykube.Node.objects(kube_cluster.kube_client)) >= 1


@pytest.mark.smoke
def test_pods_available(
    kube_cluster: Cluster, flux_deployments: List[pykube.Deployment]  # noqa: F811
) -> None:
    for d in flux_deployments:
        assert int(d.obj["status"]["readyReplicas"]) > 0
        logger.info(f"Deployment '{d.name}' is ready")


# @pytest.mark.functional
# @pytest.mark.upgrade
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

    # now we wait for the app to be deployed by flux and to run
    app_namespace = "hello-world"
    app_svc_name = "hello-world-service"
    app_deploy_name = "hello-world"
    app_svc_port = 8080
    wait_for_deployments_to_run(
        kube_cluster.kube_client,
        [app_deploy_name],
        app_namespace,
        APP_DEPLOYMENT_TIMEOUT_SEC,
    )
    app_svc: pykube.Service = pykube.Service.objects(
        kube_cluster.kube_client, namespace=app_namespace
    ).get(name=app_svc_name)

    response = app_svc.proxy_http_get("/", app_svc_port)
    assert response.status_code == 200


@pytest.mark.functional
@pytest.mark.upgrade
def test_helm_works(
        kube_cluster: Cluster,
        flux_deployments: List[pykube.Deployment],  # noqa: F811
        helm_repository_factory: HelmRepositoryFactoryFunc,  # noqa: F811
        helm_release_factory: HelmReleaseFactoryFunc,  # noqa: F811
) -> None:
    """
    This test checks if it is possible to deploy a HelmRelease with HelmRepository as a source.
    For upgrade test, the workflow is executed twice, so for both the stable and under-test versions
    a full cycle is executed (app is deployed and then destroyed).
    """
    namespace = "default"

    helm_repository_factory("giantswarm", namespace, "1m", "https://giantswarm.github.io/giantswarm-catalog")
    helm_release_factory("hello-world", namespace, chart={"chart": "hello-world-app", "version": "0.1.0"},
                         interval="1m")

    # now we wait for the app to be deployed by flux and to run
    app_namespace = "hello-world"
    app_svc_name = "hello-world-service"
    app_deploy_name = "hello-world"
    app_svc_port = 8080
    wait_for_deployments_to_run(
        kube_cluster.kube_client,
        [app_deploy_name],
        app_namespace,
        APP_DEPLOYMENT_TIMEOUT_SEC,
    )
    app_svc: pykube.Service = pykube.Service.objects(
        kube_cluster.kube_client, namespace=app_namespace
    ).get(name=app_svc_name)

    response = app_svc.proxy_http_get("/", app_svc_port)
    assert response.status_code == 200
