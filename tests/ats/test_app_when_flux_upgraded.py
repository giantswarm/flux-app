from typing import Dict

import pytest
from pytest_helm_charts.clusters import Cluster
from pytest_helm_charts.fixtures import test_extra_info  # noqa: F401
from pytest_helm_charts.flux.git_repository import make_git_repository_obj, wait_for_git_repositories_to_be_ready, \
    GitRepositoryCR
from pytest_helm_charts.flux.kustomization import make_kustomization_obj, wait_for_kustomizations_to_be_ready, \
    KustomizationCR
from pytest_helm_charts.giantswarm_app_platform.catalog import make_catalog_obj, CatalogCR

from helpers import assert_hello_world_is_running


@pytest.mark.upgrade
def test_app_unchanged_when_flux_upgraded(kube_cluster: Cluster, test_extra_info: Dict[str, str]) -> None:
    upgrade_stage_key = "ats_upgrade_test_stage"
    if upgrade_stage_key not in test_extra_info:
        pytest.fail(
            f"'--test-extra-info' argument with key '{upgrade_stage_key}' required, but not given to pytest run")
    upgrade_stage = test_extra_info[upgrade_stage_key]

    namespace = "default"
    catalog_name = "giantswarm"
    git_repo_name = "flux-app-tests"
    kustomization_name = "simple-app-cr-delivery"
    app_deploy_namespace = "hello-world"

    # we can't use fixture factories here, as they are automatically cleaned up at the end of test (the latest)
    if upgrade_stage == "pre_upgrade":
        # deploy app and leave it running
        deploy_as_kustomization(kube_cluster, app_deploy_namespace, catalog_name, git_repo_name, kustomization_name,
                                namespace)

    elif upgrade_stage == "post_upgrade":
        # check app runs then delete it
        delete_deployment(kube_cluster, catalog_name, git_repo_name, kustomization_name, namespace,
                          app_deploy_namespace)
    else:
        pytest.fail(f"Unknown value '{upgrade_stage}' given as '{upgrade_stage_key}'")


def delete_deployment(kube_cluster: Cluster, catalog_name: str, git_repo_name: str, kustomization_name: str,
                      namespace: str, app_namespace: str):
    # assert app is running as expected
    assert_hello_world_is_running(kube_cluster.kube_client, app_namespace)

    # delete the app deployment
    kustomization: KustomizationCR = KustomizationCR.objects(kube_cluster.kube_client).filter(
        namespace=namespace).get_by_name(kustomization_name)
    kustomization.delete()
    git_repo: GitRepositoryCR = GitRepositoryCR.objects(kube_cluster.kube_client).filter(
        namespace=namespace).get_by_name(git_repo_name)
    git_repo.delete()
    catalog: CatalogCR = CatalogCR.objects(kube_cluster.kube_client).filter(
        namespace=namespace).get_by_name(catalog_name)
    catalog.delete()


def deploy_as_kustomization(kube_cluster: Cluster, app_deploy_namespace: str, catalog_name: str, git_repo_name: str,
                            kustomization_name: str, namespace: str):
    catalog = make_catalog_obj(
        kube_cluster.kube_client, catalog_name, namespace, "https://giantswarm.github.io/giantswarm-catalog/"
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
    wait_for_git_repositories_to_be_ready(kube_cluster.kube_client, [git_repo_name], namespace, 60, missing_ok=True)

    kustomization = make_kustomization_obj(
        kube_cluster.kube_client,
        kustomization_name,
        namespace,
        True,
        "1m",
        f"./tests/test_cases/{kustomization_name}",
        git_repo_name,
        "2m",
        "kustomize-controller",
    )
    kustomization.create()
    wait_for_kustomizations_to_be_ready(kube_cluster.kube_client, [kustomization_name], namespace, 60, missing_ok=True)
    # check if deployed successfully
    assert_hello_world_is_running(kube_cluster.kube_client, app_deploy_namespace)
