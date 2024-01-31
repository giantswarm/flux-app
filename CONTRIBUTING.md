## Update from upstream

Updating from upstream requires `kustomize` (https://github.com/kubernetes-sigs/kustomize), `yq` (https://github.com/mikefarah/yq) and `skopeo` (https://github.com/containers/skopeo).

### Make container images available

- Look for images in the `install.yaml` in the upstream release (For example: https://github.com/fluxcd/flux2/releases/download/v0.33.0/install.yaml)
  - For example: `grep -i ' image: ' install.0.33.0.yaml`
  - Add any images not already retagged to [retagger](https://github.com/giantswarm/retagger)
- You can use `skopeo` to find the right sha digests (if they are retagged via digest and not by tag/version patters e.g.: `pattern: '>= v0.12.0'`):
  ```shell
  skopeo inspect --format "{{.Digest}}" --override-arch=amd64 --override-os=linux docker://docker.io/fluxcd/kustomize-controller:v0.16.0
  ```

### Update helm template
 
- Bump the `appVersion` in `helm/flux-app/Chart.yaml`
- From the root of the repository run `./hack/flux-manifest.sh`
  - If you need to add a new patch, simply make the change and store the `git diff` output into a file under `hack/git-patches`
