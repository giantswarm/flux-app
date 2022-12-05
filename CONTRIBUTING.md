## Update from upstream

Updating from upstream requires `kustomize` (https://github.com/kubernetes-sigs/kustomize), `yq` (https://github.com/mikefarah/yq) and `skopeo` (https://github.com/containers/skopeo).

### Make container images available

- Look for images in the `install.yaml` in the upstream release (For example: https://github.com/fluxcd/flux2/releases/download/v0.33.0/install.yaml)
  - For example: `grep -i ' image: ' install.0.33.0.yaml` 
  - Add any images not already retagged to [retagger](https://github.com/giantswarm/retagger)
    - The name rewrite rules are in `helm/flux-app/values.yaml` under `images`
    - You can double-check if the images have been retagged for example in Quay: https://quay.io/organization/giantswarm?tab=repos
- You can use `skopeo` to find the right sha digests (if they are retagged via digest and not by tag/version patters e.g.: `pattern: '>= v0.12.0'`):
  ```shell
  skopeo inspect --format "{{.Digest}}" --override-arch=amd64 --override-os=linux docker://docker.io/fluxcd/kustomize-controller:v0.16.0
  ```

### Update helm template

- Prepare CRD
  - Update Flux release under `resources` in the `hack/kustomization.yaml` file
  - Execute `kubectl kustomize hack | yq eval-all 'select(.kind == "CustomResourceDefinition")' - > helm/flux-app/crd-base/crds.yaml`
  - Execute `./hack/split-crds.sh` to move each `kind: CustomResourceDefinition` resource into its own file
  - Delete `helm/flux-app/crd-base/crds.yaml`
- Prepare resources
  - Execute `kubectl kustomize hack | yq eval-all 'select((.kind == "CustomResourceDefinition" | not) and (.kind == "Namespace" | not))' - > helm/flux-app/templates/install.yaml`
    - Please double-check that the container images have been replaced to something like `'{{ .Values.images.registry }}/{{ .Values.images.sourceController.image }}:v0.28.0'`
      If not then probably they updated the image source in upstream and you need to align the image rules in `hack/kustomization.yaml` under `images`. If so, please rerun the above command!
  - Execute `sed -i -e "/image:/b;s/'{{/{{/g" -e "/image:/b;s/}}'/}}/g" helm/flux-app/templates/install.yaml` to search and replace `'{{` with `{{` and `}}'` with `}}` in `helm/flux-app/templates/install.yaml`. But not in lines containing `image:`
- IMPORTANT: there is a "hack" that needs manual intervention every time we upgrade `install.yaml`, see: https://github.com/giantswarm/flux-app/pull/161
  ```gotemplate
  {{- if (.Values.kustomizeServiceAccount.annotations) }}
  annotations:
  {{- range $k, $v := .Values.kustomizeServiceAccount.annotations }}
    {{ $k }}: {{ $v }}
  {{- end -}}
  {{- end }}
  ```
- Bump the `appVersion` in `helm/flux-app/Chart.yaml`
