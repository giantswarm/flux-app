# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.18.0] - 2022-11-08

- Update VPA configuration

## [0.17.0] - 2022-10-28

### Added

- Add a check if VPA capabilities exist in the first place.

### Changed

- Upgrade ATS to `v0.2.9`
- Bump upstream flux toolkit version to from `v0.35.0` to `v0.36.0`. There are
  no breaking changes.
- Change resource requests & limits.

## [0.16.1] - 2022-10-11

### Added

- Mark the app as subject to two step installation procedure.

## [0.16.0] - 2022-10-04

### Changed

- Bump upstream flux toolkit version to from `v0.33.0` to `v0.35.0`.
  This upgrade comes with 1 breaking change from Flux [v0.34.0](https://github.com/fluxcd/flux2/releases/tag/v0.34.0), see: [fluxcd/flux2#3051](https://github.com/fluxcd/flux2/issues/3051).
- Change default registry in helm chart to docker.io.

## [0.15.1] - 2022-09-07

### Changed

- Make docs more clear on how to set up encryption

## [0.15.0] - 2022-08-31

### Changed

- Bump upstream flux toolkit version to from `v0.31.3` to `v0.33.0`.
  This upgrade comes with no breaking changes.
  Flux now supports distributing Kubernetes manifests, Kustomize overlays and Terraform code as OCI artifacts. For more information please see the [Flux OCI documentation].
  More details in [Flux v0.32.0] and [Flux v0.33.0] release notes.

## [0.14.0] - 2022-08-18

### Added

- Add installation note to README.md (also visible in e.g. Happa) about limitations of installing FluxCRDs and CRs at the same time

### Changed

- Revert to job based CRD installation as of `v0.12.0`

## [0.13.0] - 2022-08-01

### Changed

- Replaced Job based CRD installation with native Helm 3 CRD installation

### Removed

- Removed templated labels from CRDs because Helm 3 does not support templating the CRDs with the native way of installation

## [0.12.0] - 2022-07-13

### Changed

- Bump upstream flux toolkit version to v0.31.3.
  Breaking changes: Flux is no longer compatible with kubeconfigs using
  `client.authentication.k8s.io/v1alpha1`, this version was deprecated and
  removed in Kubernetes 1.24.
  More details in [Flux v0.31.0] release notes.

## [0.11.0] - 2022-05-26

### Changed

- Bump upstream flux toolkit version to v0.30.2.
  This app version upgrades Flux workloads and resource definitions from
  v0.27.3 to v0.30.2. The two upstream releases in between ([Flux v0.28.0] and
  [Flux v0.29.0]) contain potentially breaking changes, the main difference
  being graduating custom resource API versions. Please read linked upstream
  changelogs and [Flux Source v1beta2 API upgrade] document before performing
  an upgrade.

## [0.10.1] - 2022-05-13

### Added

- Push helm chart to OCI registry.

## [0.10.0] - 2022-03-07

### Changed

- Bump upstream flux toolkit version to 0.27.3

## [0.9.0] - 2022-02-03

### Added

- Added support for variable substitution.

## [0.8.0] - 2021-12-07

### Added

- Added functional and upgrade tests

### Changed

- Bump upstream flux toolkit version to 0.24.0 includes helm-controller fix to
reduce memory usage by downgrading Helm from 3.7.1 to 3.6.3

## [0.7.1] - 2021-11-17

### Fixed

- Fix PSP reference in ClusterRole.

## [0.7.0] - 2021-11-08

### Added

- Add Prometheus service discovery labels to flux-app

### Changed

- Bump upstream flux toolkit version to 0.21.0

## [0.6.1] - 2021-11-02

### Fixed

- Set VPA max allowed memory limit for helm-controller.

## [0.6.0] - 2021-10-27

### Added

- Add VerticalPodAutoscaler support.

## [0.5.1] - 2021-10-25

### Changed

- Allow configurability of the controller resources.

## [0.5.0] - 2021-10-20

- Bump upstream flux toolkit version to 0.19.0

## [0.4.1] - 2021-10-15

### Changed

- Update icon

## [0.4.0] - 2021-09-16

- Bump upstream flux toolkit version to 0.17.1

## [0.3.0] - 2021-06-16
- Bump upstream flux toolkit version to 0.15.0
- Use kubectl kustomize to update app
- Use EmptyDir instead of PVC
- Allow use of other providers other than Github

## [0.2.0] - 2021-06-04

- **Breaking**: Changed values `images` subkeys from snake\_case camelCase
- Bump upstream flux toolkit version to 0.7.7
- Change to main catalog

## [0.1.0] - 2021-02-04

- Initial release containing flux toolkit 0.5.9

[Unreleased]: https://github.com/giantswarm/flux-app/compare/v0.18.0...HEAD
[0.18.0]: https://github.com/giantswarm/flux-app/compare/v0.17.0...v0.18.0
[0.17.0]: https://github.com/giantswarm/flux-app/compare/v0.16.1...v0.17.0
[0.16.1]: https://github.com/giantswarm/flux-app/compare/v0.16.0...v0.16.1
[0.16.0]: https://github.com/giantswarm/flux-app/compare/v0.15.1...v0.16.0
[0.15.1]: https://github.com/giantswarm/flux-app/compare/v0.15.0...v0.15.1
[0.15.0]: https://github.com/giantswarm/flux-app/compare/v0.14.0...v0.15.0
[0.14.0]: https://github.com/giantswarm/flux-app/compare/v0.13.0...v0.14.0
[0.13.0]: https://github.com/giantswarm/flux-app/compare/v0.12.0...v0.13.0
[0.12.0]: https://github.com/giantswarm/flux-app/compare/v0.11.0...v0.12.0
[0.11.0]: https://github.com/giantswarm/flux-app/compare/v0.10.1...v0.11.0
[0.10.1]: https://github.com/giantswarm/flux-app/compare/v0.10.0...v0.10.1
[0.10.0]: https://github.com/giantswarm/flux-app/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/giantswarm/flux-app/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/giantswarm/flux-app/compare/v0.7.1...v0.8.0
[0.7.1]: https://github.com/giantswarm/flux-app/compare/v0.7.0...v0.7.1
[0.7.0]: https://github.com/giantswarm/flux-app/compare/v0.6.1...v0.7.0
[0.6.1]: https://github.com/giantswarm/flux-app/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/giantswarm/flux-app/compare/v0.5.1...v0.6.0
[0.5.1]: https://github.com/giantswarm/flux-app/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/giantswarm/flux-app/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/giantswarm/flux-app/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/giantswarm/flux-app/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/giantswarm/flux-app/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/giantswarm/flux-app/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/giantswarm/flux-app/releases/tag/v0.1.0

[Flux v0.28.0]: https://github.com/fluxcd/flux2/releases/tag/v0.28.0
[Flux v0.29.0]: https://github.com/fluxcd/flux2/releases/tag/v0.29.0
[Flux v0.31.0]: https://github.com/fluxcd/flux2/releases/tag/v0.31.0
[Flux v0.32.0]: https://github.com/fluxcd/flux2/releases/tag/v0.33.0
[Flux v0.33.0]: https://github.com/fluxcd/flux2/releases/tag/v0.33.0

[Flux Source v1beta2 API upgrade]: https://github.com/fluxcd/flux2/discussions/2567
[Flux OCI documentation]: https://fluxcd.io/flux/cheatsheets/oci-artifacts/
