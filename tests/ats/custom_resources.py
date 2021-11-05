from pykube.objects import NamespacedAPIObject


class GitRepositoryCR(NamespacedAPIObject):
    version = "source.toolkit.fluxcd.io/v1beta1"
    endpoint = "gitrepos"
    kind = "GitRepository"


class KustomizationCR(NamespacedAPIObject):
    version = "source.toolkit.fluxcd.io/v1beta1"
    endpoint = "kustomizations"
    kind = "Kustomization"
