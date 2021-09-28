#!/bin/bash


## Works on linux (tm). needs probably GNU grep, sed

set -uo pipefail
trap 's=$?; echo "$0: Error on line "$LINENO": $BASH_COMMAND"; exit $s' ERR
IFS=$'\n\t'

crd_names="$(yq eval '.spec.names.singular' helm/flux-app/crds/crds.yaml | grep -v -e '---')"

# count=0
for name in $crd_names
do
  # count=$((count+1))
  echo "writing ${name}.yaml"
  # extract everything up until --- into a new file
  sed -n -e '1,/^---/p' helm/flux-app/crds/crds.yaml | grep -v -e '^---$' > "helm/flux-app/crds/${name}.yaml"
  # remove everything from --- into the same file
  # super crude, if some sed wizard could improve this, I would be grateful
  sed -n '/---$/,$p' helm/flux-app/crds/crds.yaml | tail -n +2 > helm/flux-app/crds/crds-tmp.yaml
  mv helm/flux-app/crds/crds-tmp.yaml helm/flux-app/crds/crds.yaml
done