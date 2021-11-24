import abc

from pykube.objects import NamespacedAPIObject


# just to serve as a common interface
class NamespacedFluxCR(NamespacedAPIObject, abc.ABC):
    pass


class GitRepositoryCR(NamespacedFluxCR):
    version = "source.toolkit.fluxcd.io/v1beta1"
    endpoint = "gitrepositories"
    kind = "GitRepository"


class KustomizationCR(NamespacedFluxCR):
    version = "kustomize.toolkit.fluxcd.io/v1beta1"
    endpoint = "kustomizations"
    kind = "Kustomization"
