import logging
from typing import List

import pykube
import pytest
from pytest_helm_charts.fixtures import Cluster

# noinspection PyUnresolvedReferences
from fixtures import flux_deployments  # noqa: F104
from utils import get_git_repository_obj, get_kustomize_obj

logger = logging.getLogger(__name__)


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
def test_pods_available(kube_cluster: Cluster, flux_deployments: List[pykube.Deployment]) -> None:
    for d in flux_deployments:
        assert int(d.obj["status"]["readyReplicas"]) > 0
        logger.info(f"Deployment '{d.name}' is ready")


@pytest.mark.functional
def test_kustomization_works(kube_cluster: Cluster, flux_deployments: List[pykube.Deployment]) -> None:
    git_repo_cr_name = "flux-app-tests"
    # todo: turn into fixture
    git_repo = get_git_repository_obj(kube_cluster.kube_client, git_repo_cr_name, "default",
                                      "1m", "https://github.com/giantswarm/flux-app-tests",
                                      "feature/init-with-data", ignore_pattern="tests/test_cases/**/result")
    git_repo.create()
    # TODO: wait for repo to be ready
    test_name = "simple-app-cr-delivery"
    # todo: turn into fixture
    ks = get_kustomize_obj(kube_cluster.kube_client, test_name, "default",
                           True, "1m", f"./tests/test_cases/{test_name}", git_repo_cr_name, "2m")
    ks.create()
    # TODO: wait for kustomization to show up

    # now we wait for the app to run

    ks.delete()
    git_repo.delete()
