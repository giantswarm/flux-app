#!/usr/bin/env bash
# ---------------------------------------------------------------------
# This script is supposed to get the yaml file from the flux release,
# patch and by applying patches turn it to the helm chart.
# ---------------------------------------------------------------------
# 1. We need to prepare the environment first. The version of the
#    release is taken from the helm chart properties.
#    So if you want to try patching a newer release, you'll have to
#    bump the .appVersion of the chart
VERSION=$(yq '.appVersion' ./helm/flux-app/Chart.yaml)
# The whole preparation will be happening in a temporary folder, hence
# these dir related variables
CURRENT_DIR=$(pwd)
CHART_DIR="${CURRENT_DIR}/helm/flux-app"
CRDS_DIR="${CHART_DIR}/crd-base"
WORKDIR=$(mktemp -d)
echo "workdir is $WORKDIR"
cd $WORKDIR
# ---------------------------------------------------------------------
# Download the official flux installation manifest
# ---------------------------------------------------------------------
curl -s -L "https://github.com/fluxcd/flux2/releases/download/v${VERSION}/install.yaml" \
    | yq -s '.kind + "-" + .metadata.name'
# ---------------------------------------------------------------------
# Remove the namespace manifest
# We don't want to have a namespace as a part of this helm chart
# so it should be removed
# --------------------------------------------------------------------
for ns in $(find . -type f -name "Namespace*"); do
    rm -f $ns
done
# ---------------------------------------------------------------------
# And here goes the main part. 
# Since we have regular yaml files, we need to
# turn them into helm templates. Currently, it's done by git patches,
# but I'm not sure how versatile this approach is. We will only see
# when newer flux version will be released and we will try to patch it
#
# The tricky part here is to set correct images in the release, and
# images are a subject to be change on each release.
# That's why we need to patch patches.
#
# > Personally, I don't like that, because it seems like becoming
# >   a real legacy code right off the bat, so if you have a better
# >   solution, please change it
# >                                                     @allanger
#
# ---------------------------------------------------------------------
# Here we are preparing files and removing namespaces from each file
# I've chosen to do it this way, because it should be very stable,
# because yq will definetely find namespaces will definetely remove
# them, so it's not a git patch
# ---------------------------------------------------------------------
TEMPLATES_DIR="${CURRENT_DIR}/helm/flux-app/templates/base"
# ---------------------------------------------------------------------
# Here goes this patch patching thingy
# ---------------------------------------------------------------------
for template in $(find . -type f); do
    yq e -i 'del(.metadata.namespace)' $template
    TARGET_FILE_NAME="$(echo $template | grep -o -P '(?<=/).*?(?=\.)' \
        | tr '[:upper:]' '[:lower:]' ).yaml"
    mv $template "$TARGET_FILE_NAME"
done

ls 
# ---------------------------------------------------------------------
# Now, let's prepare a patch for images. Since the amount of containers
# is pretty much defined, we will just export some variables and then
# put their values in the patch
# ---------------------------------------------------------------------
export CMD="yq '.spec.template.spec.containers.[] | select(.name == \"manager\") | .image'"
export IMAGE_HELM_CTRL=$(bash -c "$CMD deployment-helm-controller.yaml")
export IMAGE_AUTOMATION_CTRL=$(bash -c "$CMD deployment-image-automation-controller.yaml")
export IMAGE_REFLECTOR_CTRL=$(bash -c "$CMD deployment-image-reflector-controller.yaml")
export IMAGE_KUSTOMIZE_CTRL=$(bash -c "$CMD deployment-kustomize-controller.yaml")
export IMAGE_NOTIFICATION_CTRL=$(bash -c "$CMD deployment-notification-controller.yaml")
export IMAGE_SOURCE_CTRL=$(bash -c "$CMD deployment-source-controller.yaml")
env | grep IMAGE
IMAGES_PATCH=$CURRENT_DIR/hack/git-patches/7-images.patch
envsubst < "$IMAGES_PATCH.tmpl" > $IMAGES_PATCH
# ---------------------------------------------------------------------
# Patch resources finally. I'm creating patches that should be applied
# in the exact order, so names are prefixed with numbers. It wasn't
# designed in that order, it was just a way of thoughts.
# ---------------------------------------------------------------------
git init . && git add . && git commit -m "Init commit"
for patch in $(find "$CURRENT_DIR/hack/git-patches" -type f -name "*.patch" | sort); do
    echo "applying $patch"
    git apply $patch
done
# ---------------------------------------------------------------------
# If you want to add a new patch based on your changes inside
# the base dir, uncomment this block of code and run it. It will create
# a tmp.patch that you'll have to rename. After it's renamved, comment
# it back out, and run again
# ---------------------------------------------------------------------
#TMP_DIR=$(mktemp -d)
#echo "temporary dir is $TMP_DIR"
#cp $CURRENT_DIR/helm/flux-app/crd-base/* $TMP_DIR
#cp $CURRENT_DIR/helm/flux-app/templates/base/* $TMP_DIR
#git add .
#cp $TMP_DIR/* .
#git diff . > $CURRENT_DIR/hack/git-patches/tmp.patch
#exit 0
# ---------------------------------------------------------------------
rm -rf "${TEMPLATES_DIR}" && mkdir "${TEMPLATES_DIR}"
# ---------------------------------------------------------------------
# Copy patched files to our chart ant that's it
# ---------------------------------------------------------------------
rm -rf .git
# ---------------------------------------------------------------------
# After we got manifests, we want to extract CRDs, because they will
# be treated differently
# Old CRDs will be removed and replaces by newer ones
# ---------------------------------------------------------------------
rm -rf $CRDS_DIR && mkdir $CRDS_DIR
for crd in $(find . -type f -name "customresource*"); do
    mv $crd "$CRDS_DIR"
done
for template in $(find . -type f); do
    cp $template "$TEMPLATES_DIR"
done
# ---------------------------------------------------------------------
# -- Cleanup
# ---------------------------------------------------------------------
rm -rf $WORKDIR
rm -f $IMAGES_PATCH
cd $CURRENT_DIR
