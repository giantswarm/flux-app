[![CircleCI](https://circleci.com/gh/giantswarm/flux-app.svg?style=shield)](https://circleci.com/gh/giantswarm/flux-app)

# flux-app chart

Giant Swarm offers a flux Managed App which can be installed in tenant clusters.
Here we define the flux chart with its templates and default configuration.

It can be used to install [flux2](https://github.com/flux/flux2).

## Update from upstream

First, check the [upstream releases page](https://github.com/fluxcd/flux2/releases) and copy the `manifests.tar.gz` URL.`

Check out [`hack/sync.sh`](https://github.com/giantswarm/flux-app/blob/master/hack/sync.sh). It can be used to fetch updated manifests from upstream with manifests in this repository.

Edit `hack/sync.sh` and replace the `upstream_manifests_url` value with the URL from the upstream releases page.

```bash
# Execute ./hack/sync.sh form the root of the repository
./hack/sync.sh
```

Any previous changes are recorded in patch files residing in the [`patch`](https://github.com/giantswarm/flux-app/tree/master/patch) directory and will be applied through the script.

After you've executed the `sync.sh` script, do the following:

- Examine the changes, don't commit anything yet
- `git add -A helm/flux-app`
- If you see stuff you need to change, make a commit now without doing anything yet.
- Make your changes, but don't `git add` them yet
- Create a patch of your changes. `git -C helm/gatekeeper-app diff --relative | tee patch/XX.foo.patch` (Set XXX to the next available integer, patches are applied sequentially)
- Stage and commit everything
- To verify everything is ok, re-run the sync script

This workflow and script is heavily inspired by the script in [gatekeeper-app](https://github.com/giantswarm/gatekeeper-app).

## Credit

* {APP HELM REPOSITORY}
