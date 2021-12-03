import pykube
from pykube import HTTPClient
from pytest_helm_charts.utils import wait_for_deployments_to_run

APP_DEPLOYMENT_TIMEOUT_SEC = 180


def assert_hello_world_is_running(kube_client: HTTPClient, app_namespace: str):
    app_svc_name = "hello-world-service"
    app_deploy_name = "hello-world"
    app_svc_port = 8080
    wait_for_deployments_to_run(
        kube_client,
        [app_deploy_name],
        app_namespace,
        APP_DEPLOYMENT_TIMEOUT_SEC,
    )
    app_svc: pykube.Service = pykube.Service.objects(kube_client, namespace=app_namespace).get(name=app_svc_name)
    response = app_svc.proxy_http_get("/", app_svc_port)
    assert response.status_code == 200
