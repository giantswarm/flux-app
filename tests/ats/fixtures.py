import pykube
import pytest
from pytest_helm_charts.clusters import Cluster
from pytest_helm_charts.utils import wait_for_deployments_to_run

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
