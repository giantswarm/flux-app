[![CircleCI](https://circleci.com/gh/giantswarm/flux-app.svg?style=shield)](https://circleci.com/gh/giantswarm/flux-app)

# Flux Helm Chart

Giant Swarm offers a flux Managed App which can be installed in tenant clusters.
Here we define the flux chart with its templates and default configuration.

It can be used to install [flux2](https://github.com/fluxcd/flux2) toolkit.

## Important installation notes

If you want to install the Flux CRDs - `crds.install` value, enabled by default - and your Flux CRs as well,
then you need to install the App in 2 steps. First install without the CRs so Helm can create the Flux CRDs
for you. Then in a following apply of the App add your Flux CRs - `sources` and `kustomizations` values.

The reason for this is how Helm manages CRDs and validation of manifests before it applies them to the cluster.
You cannot install CRDs and CRs using those CRDs in the same run as Helm will fail to validate the manifests against
the API. It is possible with the [Helm 3 native way of installing CRDs](https://helm.sh/docs/chart_best_practices/custom_resource_definitions/)
but that does not support updating them in the future. Therefore, we install the CRDs using a Job which solves
upgrading the CRDs but does not solve installing them at the same time with CRs using those CRDs. In theory the CRs
could be installed with a separate Job as well but then those resources are not managed by Helm and would require
and another Job upon uninstallation to get cleaned up but this adds a lot a complexity and the risk of deleting
resources that were not intended to be deleted by the post install hook of the CR clean-up.

## Values & Secrets

This chart allows to add flux `GitRepository` and `Kustomization` CRs through `values.yaml`

You need to create a GitHub token.

Example yaml:

```yaml
sources:
- kind: GitRepository
  name: my-git-source
  url: https://github.com/my-org/my-repo.git
  provider: github
  credentials:
    username: my-username
    password: github-token
  interval: 1m0s
  branch: the-branch
kustomizations:
- name: my-kustomization
  source_name: my-git-source
  path: ./the-path
  postBuild:
    substitute:
      environment: "my-env"
    substituteFrom:
      - kind: ConfigMap
        name: my-env-vars
  prune: false
  interval: 10m0s
```

## Encrypt Kubernetes Secrets in a Git repository using Mozilla SOPS

Since your configuration will sometimes contain sensitive data, flux provides several mechanisms to store and handle that data securely.
This chart is able to install a gpg secret key for usage with sops. The public key from that same secret can then be used to encrypt the sensitive parts of your configuration, while flux will be able to decrypt it when pulling the configuration.

For this to work, export your secret key using `gpg --export-secret-keys --armor <your-gpg-key-id>`.

```
sopsEncryption:
  enabled: true
  encryptionKeys:
    - |
      <output of gpg --export-secret-keys --armor <your-gpg-key-id>>
    - |
      <output of gpg --export-secret-keys --armor <your-other-gpg-key-id>>
```

This is the SOPS configuration part for `flux-app`. Now we need to set it up as a [user secret for App Platform](https://docs.giantswarm.io/app-platform/app-configuration/#example-secret).

Take the above piece of configuration and base64 encode it and save it in a file called let's say `user-secret.yaml`.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: sops-gpg
  namespace: my-namespace
data:
  values: "<<BASE64_ENCODED_CONFIGURATION_WITH_SECRETS>>"
```

Then encrypt your secrets using SOPS.

```shell
sops --encrypt \
     --pgp=<your-gpg-key-id> \
     --encrypted-regex '^(data|stringData)$' \
     --in-place user-secret.yaml
```

Finally, you should reference the secret in your App CR:

```yaml

apiVersion: application.giantswarm.io/v1alpha1
kind: App
metadata:
  labels:
    app.kubernetes.io/name: flux-app
  name: flux-app
  namespace: my-namespace
spec:
  # ...
  userConfig:
    secret:
      name: sops-gpg
      namespace: my-namespace
```

The App configuration layers will be merged together by the App Platform. You can read more about layer, merging order and example [here](https://docs.giantswarm.io/app-platform/app-configuration/).

You can read more about managing secrets with Flux [here](https://toolkit.fluxcd.io/guides/mozilla-sops/).

### Add additional keys to the encrypted secret

This example shows how to import a gpg key into your local keychain and add it to a secret.

- Import public key `gpg --import file-with-public-key` (Exported using `gpg --export --armor KEYID`)
- `sops updatekeys filename`. This requires a [`.sops.yaml`](https://github.com/mozilla/sops/tree/38b25bd449619e1d6da20e637702f7c73203aa44#updatekeys-command) file which contains all pgp key ids.

To change the encrypted file, one must have all public keys in their keychain. Then its possible to use `sops filename` to change the contents of the file.

### Hints

- When encrypting secrets with SOPS, it's possible to use a 'common' gpg key which is only used for decryption on the cluster. Just add the key id to the `.sops.yaml` file and update the keys used as described in the section above. Now only the private key of the 'common' key needs to be present on the cluster.

## Contributing

Please refer to the [contributing guide](https://github.com/giantswarm/flux-app/blob/master/CONTRIBUTING.md).
