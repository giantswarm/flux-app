#!/usr/bin/env bash

kubectl kustomize hack | yq eval-all 'select((.kind == "CustomResourceDefinition" | not) and (.kind == "Namespace" | not))' > helm/flux-app/templates/install.yaml

sed -i 's!GS_PLACEHOLDER_RESOURCES_HELM_CONTROLLER!\n{{ include "resources.helmController" . | indent 12 }}!g' helm/flux-app/templates/install.yaml
sed -i 's!GS_PLACEHOLDER_RESOURCES_IMAGE_AUTOMATION_CONTROLLER!\n{{ include "resources.imageAutomationController" . | indent 12 }}!g' helm/flux-app/templates/install.yaml
sed -i 's!GS_PLACEHOLDER_RESOURCES_IMAGE_REFLECTOR_CONTROLLER!\n{{ include "resources.imageReflectorController" . | indent 12 }}!g' helm/flux-app/templates/install.yaml
sed -i 's!GS_PLACEHOLDER_RESOURCES_KUSTOMIZE_CONTROLLER!\n{{ include "resources.kustomizeController" . | indent 12 }}!g' helm/flux-app/templates/install.yaml
sed -i 's!GS_PLACEHOLDER_RESOURCES_NOTIFICATION_CONTROLLER!\n{{ include "resources.notificationController" . | indent 12 }}!g' helm/flux-app/templates/install.yaml
sed -i 's!GS_PLACEHOLDER_RESOURCES_SOURCE_CONTROLLER!\n{{ include "resources.sourceController" . | indent 12 }}!g' helm/flux-app/templates/install.yaml

sed -i -e "/image:/b;s/'{{/{{/g" -e "/image:/b;s/}}'/}}/g" helm/flux-app/templates/install.yaml