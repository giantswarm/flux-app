import logging
from typing import List

import pykube
import pytest

from pytest_helm_charts.flux.fixtures import flux_deployments  # noqa: F401
from pytest_helm_charts.clusters import Cluster

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
