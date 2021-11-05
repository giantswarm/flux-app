from pykube.objects import NamespacedAPIObject


class GitRepositoryCR(NamespacedAPIObject):
    version = "source.toolkit.fluxcd.io/v1beta1"
    endpoint = "gitrepositories"
    kind = "GitRepository"


class KustomizationCR(NamespacedAPIObject):
    version = "kustomize.toolkit.fluxcd.io/v1beta1"
    endpoint = "kustomizations"
    kind = "Kustomization"