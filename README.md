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

## Encrypt Kubernetes Secrets in a Git repository using Mozilla SOPS

This chart is able to install a gpg secret key for usage with sops.

For this to work, export your secret key using `gpg --export-secret-keys --armor <your-gpg-key-id>`. Then specify it in your values.yaml like this (its possible to specify multiple keys):

```
sopsEncryption:
  enabled: true
  encryptionKeys:
    - |
      <output of gpg --export-secret-keys \
          --armor <your-gpg-key-id>>
    - |
      <output of gpg --export-secret-keys \
          --armor <your-other-gpg-key-id>>
```

Then encrypt your secrets using the method described below (`In your Git repository create Secrets as usual`).

Original documentation: [https://toolkit.fluxcd.io/guides/mozilla-sops/](https://toolkit.fluxcd.io/guides/mozilla-sops/)

### TL;DR manually:

- Install [sops](https://github.com/mozilla/sops/releases)
- Create a Secret containing your public and private keypair

      gpg --export-secret-keys \
        --armor <your-gpg-key-id> |
      kubectl create secret generic sops-gpg \
        --namespace=<your-flux-namespace> \
        --from-file=sops.asc=/dev/stdin

- In your Git repository create Secrets as usual, but encrypt them using `sops`

      kubectl -n default create secret generic basic-auth \
        --from-literal=user=admin \
        --from-literal=password=change-me \
        --dry-run=client \
        -o yaml > basic-auth.yaml

      sops --encrypt \
        --pgp=<your-gpg-key-id> \
        --encrypted-regex '^(data|stringData)$' \
        --in-place basic-auth.yaml

- Your Kustomization should reference the `sops-gpg` secret for decryption

      apiVersion: kustomize.toolkit.fluxcd.io/v1beta1
      kind: Kustomization
      metadata:
        name: my-kustomization
        namespace: my-namespace
      spec:
        ...stuff not relevant for this example...
        decryption:
          provider: sops
          secretRef: sops-gpg

### Add additional keys to the encrypted secret

This example shows how to import a gpg key into your local keychain and add it to a secret.

- Import public key `gpg --import file-with-public-key` (Exported using `gpg --export --armor KEYID`)
- `sops updatekeys filename`. This requires a [`.sops.yaml`](https://github.com/mozilla/sops/tree/38b25bd449619e1d6da20e637702f7c73203aa44#updatekeys-command) file which contains all pgp key ids.

To change the encrypted file, one must have all public keys in their keychain. Then its possible to use `sops filename` to change the contents of the file.

### Hints

It's possible to use a 'common' gpg key which is only used for decryption on the cluster. Just add the key id to the `.sops.yaml` file and update the keys used as described in the section above. Now only the private key of the 'common' key needs to be present on the cluster.

## Update from upstream

Updating from upstream requires `kustomize` (https://github.com/kubernetes-sigs/kustomize) and `yq` (https://github.com/mikefarah/yq).

- Look for images in the `install.yaml` in the upstream release. Add any images not already retagged to [retagger](https://github.com/giantswarm/retagger)
- Prepare CRD
  - Comment out the `transformers` in the `hack/kustomization.yaml` file
  - Execute `kustomize build hack | yq eval-all 'select(.kind == "CustomResourceDefinition")' - > helm/flux-app/crds/crds.yaml`
  - Move each `kind: CustomResourceDefinition` resource into an own file
  - Delete `helm/flux-app/crds/crds.yaml`
- Prepare resources
  - Restore the `transformers` in `hack/kustomization.yaml`
  - Execute `kustomize build hack | yq eval-all 'select((.kind == "CustomResourceDefinition" | not) and (.kind == "Namespace" | not))' - > helm/flux-app/templates/install.yaml`
  - Execute `sed -i -e "/image:/b;s/'{{/{{/g" -e "/image:/b;s/}}'/}}/g" helm/flux-app/templates/install.yaml` to search and replace `'{{` with `{{` and `}}'` with `}}` in `helm/flux-app/templates/install.yaml`. But not in lines containing `image:`
- Bump the `appVersion` in `helm/flux-app/Chart.yaml`
