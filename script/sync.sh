#!/bin/bash

## sync with upstream
# tested on linux

set -uo pipefail
trap 's=$?; echo "$0: Error on line "$LINENO": $BASH_COMMAND"; exit $s' ERR
IFS=$'\n\t'

# Upstream manifests url
upstream_manifests_url=https://github.com/fluxcd/flux2/releases/download/v0.3.0/manifests.tar.gz
# Path to helm chart in this repository, relative to this script
local_chart_path="../helm/flux-app/"
# Path to patch files in this repository, relative to this script
patch_files="../patch/*.patch"


script_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd -P)"
tmp=$(mktemp -d)
# Clean temporary directory on exit
#trap "rm -rf ${tmp}" EXIT

echo "=====> fetching upstream manifests"

mkdir -p "${tmp}/templates"

curl -SL "${upstream_manifests_url}" | tar -C "${tmp}/templates" -xvzf -

echo "=====> patching chart"
for file in $script_path/$patch_files; do
    patch -p1 -d "${tmp}" < $file
done

echo "=====> copying new manifests"
rsync -av "$tmp/" "$script_path/$local_chart_path"


echo "=====> done"
