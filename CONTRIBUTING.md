## Update from upstream

Updating from upstream requires `kustomize` (https://github.com/kubernetes-sigs/kustomize), `yq` (https://github.com/mikefarah/yq) and `skopeo` (https://github.com/containers/skopeo).

### Make container images available

- Look for images in the `install.yaml` in the upstream release. Add any images not already retagged to [retagger](https://github.com/giantswarm/retagger)
- You can use `skopeo` to find the right sha digests

     skopeo inspect --format "{{.Digest}}" --override-arch=amd64 --override-os=linux docker://docker.io/fluxcd/kustomize-controller:v0.16.0

### Update helm template

- Prepare CRD
  - Comment out the `transformers` in the `hack/kustomization.yaml` file
  - Execute `kubectl kustomize hack | yq eval-all 'select(.kind == "CustomResourceDefinition")' - > helm/flux-app/crds/crds.yaml`
  - Execute `./hack/split-crds.sh` to move each `kind: CustomResourceDefinition` resource into its own file
  - Delete `helm/flux-app/crds/crds.yaml`
- Prepare resources
  - Restore the `transformers` in `hack/kustomization.yaml`
  - Execute `kubectl kustomize hack | yq eval-all 'select((.kind == "CustomResourceDefinition" | not) and (.kind == "Namespace" | not))' - > helm/flux-app/templates/install.yaml`
  - Execute `sed -i -e "/image:/b;s/'{{/{{/g" -e "/image:/b;s/}}'/}}/g" helm/flux-app/templates/install.yaml` to search and replace `'{{` with `{{` and `}}'` with `}}` in `helm/flux-app/templates/install.yaml`. But not in lines containing `image:`
- Bump the `appVersion` in `helm/flux-app/Chart.yaml`
