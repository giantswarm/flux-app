# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/giantswarm/flux-app/compare/v0.7.1...HEAD
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
