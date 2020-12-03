#!/bin/bash

## sync with upstream
# tested on linux

set -uo pipefail
trap 's=$?; echo "$0: Error on line "$LINENO": $BASH_COMMAND"; exit $s' ERR
IFS=$'\n\t'

# Upstream manifests url
upstream_manifests_url=https://github.com/fluxcd/flux2/releases/download/v0.4.2/manifests.tar.gz
# Path to helm chart in this repository, relative to this script
local_chart_path="../helm/flux-app/"

script_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd -P)"
tmp=$(mktemp -d)
# Clean temporary directory on exit
trap 'rm -rf ${tmp}' EXIT

echo "=====> fetching upstream manifests"

mkdir -p "${tmp}/manifests"
mkdir -p "${tmp}/kustomization"
mkdir -p "${tmp}/templates"

curl -SL "${upstream_manifests_url}" | tar -C "${tmp}/manifests" -xvzf -

find "${tmp}/manifests/" -name "*.yaml" | while read -r file; do
  filename="${file##*/}"
  echo "kustomizing ${filename}"
  cp "${file}" "${tmp}/kustomization/${filename}"
  sed "/^resources:$/a - ./${filename}" "${script_path}/kustomization.yaml" > "${tmp}/kustomization/kustomization.yaml"
  kustomize build "${tmp}/kustomization" > "${tmp}/templates/${filename}"
  rm "${tmp}/kustomization/kustomization.yaml"
done

rm -rf "${tmp}/manifests"
rm -rf "${tmp}/kustomization"

echo "=====> copying new manifests"

rsync -av "$tmp/" "$script_path/$local_chart_path"

echo "=====> done"
