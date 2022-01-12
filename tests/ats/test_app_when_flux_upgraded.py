import os
from os.path import exists
from typing import Dict

import pytest
from pykube import Deployment
from pytest_helm_charts.clusters import Cluster
from pytest_helm_charts.flux.git_repository import (
    make_git_repository_obj,
    wait_for_git_repositories_to_be_ready,
    GitRepositoryCR,
)
from pytest_helm_charts.flux.kustomization import (
    make_kustomization_obj,
    wait_for_kustomizations_to_be_ready,
    KustomizationCR,
)
from pytest_helm_charts.giantswarm_app_platform.catalog import (
    make_catalog_obj,
    CatalogCR,
)

from helpers import assert_hello_world_is_running


# this file doesn't have to be protected and needs to have a constant name
tmp_file_name = "/tmp/pytest-helm-charts-flux-app-upgrade-test-generation.txt"  # nosec


@pytest.mark.upgrade
def test_app_unchanged_when_flux_upgraded(
    kube_cluster: Cluster, test_extra_info: Dict[str, str]
) -> None:
    upgrade_stage_key = "ats_upgrade_test_stage"
    if upgrade_stage_key not in test_extra_info:
        pytest.fail(
            f"'--test-extra-info' argument with key '{upgrade_stage_key}' required, but not given to pytest run"
        )
    upgrade_stage = test_extra_info[upgrade_stage_key]

    namespace = "default"
    suffix = "-flux-app-upgrade-test"
    catalog_name = "giantswarm" + suffix
    git_repo_name = "flux-app-tests" + suffix
    test_dir_name = "simple-app-cr-upgrade"
    kustomization_name = test_dir_name + suffix
    app_deploy_namespace = "hello-world" + suffix
    deployment_name = "hello-world-flux-app-upgrade-test"

    # we can't use fixture factories here, as they are automatically cleaned up at the end of test (the latest)
    if upgrade_stage == "pre_upgrade":
        # deploy app and leave it running
        deploy_as_kustomization(
            kube_cluster,
            app_deploy_namespace,
            catalog_name,
            git_repo_name,
            kustomization_name,
            namespace,
            test_dir_name,
            deployment_name,
        )

    elif upgrade_stage == "post_upgrade":
        # check app runs then delete it
        delete_deployment(
            kube_cluster,
            catalog_name,
            git_repo_name,
            kustomization_name,
            namespace,
            app_deploy_namespace,
            deployment_name,
        )
    else:
        pytest.fail(f"Unknown value '{upgrade_stage}' given as '{upgrade_stage_key}'")


def delete_deployment(
    kube_cluster: Cluster,
    catalog_name: str,
    git_repo_name: str,
    kustomization_name: str,
    namespace: str,
    app_namespace: str,
    deployment_name: str,
):
    # assert app is running as expected
    assert_hello_world_is_running(
        kube_cluster.kube_client,
        app_namespace,
        app_deploy_name="hello-world-flux-app-upgrade-test",
        app_svc_name="hello-world-flux-app-upgrade-test-service",
    )
    if not exists(tmp_file_name):
        pytest.fail(
            f"The expected tmp file with Deployment generation info not found at path: '{tmp_file_name}'"
        )
    deployment_generation = get_deployment_generation(
        kube_cluster, deployment_name, app_namespace
    )
    with open(tmp_file_name, "r") as f:
        expected_generation = f.read()
    os.remove(tmp_file_name)
    assert deployment_generation == expected_generation

    # delete the app deployment
    kustomization: KustomizationCR = (
        KustomizationCR.objects(kube_cluster.kube_client)
        .filter(namespace=namespace)
        .get_by_name(kustomization_name)
    )
    kustomization.delete()
    git_repo: GitRepositoryCR = (
        GitRepositoryCR.objects(kube_cluster.kube_client)
        .filter(namespace=namespace)
        .get_by_name(git_repo_name)
    )
    git_repo.delete()
    catalog: CatalogCR = (
        CatalogCR.objects(kube_cluster.kube_client)
        .filter(namespace=namespace)
        .get_by_name(catalog_name)
    )
    catalog.delete()


def deploy_as_kustomization(
    kube_cluster: Cluster,
    app_deploy_namespace: str,
    catalog_name: str,
    git_repo_name: str,
    kustomization_name: str,
    namespace: str,
    test_dir_name: str,
    deployment_name: str,
):
    catalog = make_catalog_obj(
        kube_cluster.kube_client,
        catalog_name,
        namespace,
        "https://giantswarm.github.io/giantswarm-catalog/",
    )
    catalog.create()
    git_repository = make_git_repository_obj(
        kube_cluster.kube_client,
        git_repo_name,
        namespace,
        "1m",
        "https://github.com/giantswarm/flux-app-tests",
        "main",
        ignore_pattern="tests/test_cases/**/result",
    )
    git_repository.create()
    wait_for_git_repositories_to_be_ready(
        kube_cluster.kube_client, [git_repo_name], namespace, 60, missing_ok=True
    )

    kustomization = make_kustomization_obj(
        kube_cluster.kube_client,
        kustomization_name,
        namespace,
        True,
        "1m",
        f"./tests/test_cases/{test_dir_name}",
        git_repo_name,
        "2m",
        "kustomize-controller",
    )
    kustomization.create()
    wait_for_kustomizations_to_be_ready(
        kube_cluster.kube_client, [kustomization_name], namespace, 60, missing_ok=True
    )
    # check if deployed successfully
    assert_hello_world_is_running(
        kube_cluster.kube_client,
        app_deploy_namespace,
        app_deploy_name="hello-world-flux-app-upgrade-test",
        app_svc_name="hello-world-flux-app-upgrade-test-service",
    )
    deployment_generation = get_deployment_generation(
        kube_cluster, deployment_name, app_deploy_namespace
    )
    try:
        with open(tmp_file_name, "w") as f:
            f.write(deployment_generation)
    except Exception as e:
        print(e)


def get_deployment_generation(kube_cluster, deployment_name, namespace) -> str:
    hello_deployment: Deployment = (
        Deployment.objects(kube_cluster.kube_client)
        .filter(namespace=namespace)
        .get_by_name(deployment_name)
    )
    return str(hello_deployment.obj["status"]["observedGeneration"])
