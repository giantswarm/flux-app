[![CircleCI](https://circleci.com/gh/giantswarm/flux-app.svg?style=shield)](https://circleci.com/gh/giantswarm/flux-app)

# flux chart

Giant Swarm offers a flux Managed App which can be installed in tenant clusters.
Here we define the flux chart with its templates and default configuration.

It can be used to install [flux2](https://github.com/flux/flux2).

## Values & Secrets

This chart allows to add flux `GitRepository` and `Kustomization` CRs through `values.yaml`

You need to create a GitHub token.

Example yaml:

```yaml
sources:
- kind: GitRepository
  name: my-git-source
  url: https://github.com/my-org/my-repo.git
  credentials:
    username: my-username
    password: github-token
  interval: 1m0s
  branch: the-branch
kustomizations:
- name: my-kustomization
  source_name: my-git-source
  path: ./the-path
  prune: false
  interval: 10m0s
```

## Update from upstream

Updating from upstream requires `kustomize`.

- Look for images in the `install.yaml` in the upstream release. Add any images not already retagged to [retagger](https://github.com/giantswarm/retagger)
- Prepare CRD
  - Comment out the `commonLabels` in the `hack/kustomization.yaml` file
  - Execute `kustomize build hack > helm/flux-app/crds/crds.yaml`
  - Delete the `kind: Namespace` part from `helm/flux-app/crds/crds.yaml`
  - Move each `kind: CustomResourceDefinition` resource into an own file
  - Discard everything else
- Prepare resources
  - Restore the `commonLabels` in `hack/kustomization.yaml`
  - Execute `kustomize build hack > helm/flux-app/templates/install.yaml`
  - Delete the `kind: Namespace` part
  - Delete every `kind: CustomResourceDefinition` parts
  - Search and replace the `'` quotes in all label values in `helm/flux-app/templates/install.yaml`
- Bump the `appVersion` in `helm/flux-app/Chart.yaml`
