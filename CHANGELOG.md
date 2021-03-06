# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/giantswarm/flux-app/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/giantswarm/flux-app/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/giantswarm/flux-app/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/giantswarm/flux-app/releases/tag/v0.1.0
