{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "labels.common" -}}
{{ include "labels.selector" . }}
app.kubernetes.io/managed-by: {{ .Release.Service | quote }}
application.giantswarm.io/team: {{ index .Chart.Annotations "application.giantswarm.io/team" | quote }}
helm.sh/chart: {{ include "chart" . | quote }}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "labels.selector" -}}
app.kubernetes.io/name: {{ include "name" . | quote }}
app.kubernetes.io/instance: {{ .Release.Name | quote }}
{{- end -}}

{{- define "crdInstall" -}}
{{- printf "%s-%s" ( include "name" . ) "crd-install" | replace "+" "_" | trimSuffix "-" -}}
{{- end -}}

{{- define "crdInstallJob" -}}
{{- printf "%s-%s-%s" ( include "name" . ) "crd-install" .Chart.AppVersion | replace "+" "_" | replace "." "-" | trimSuffix "-" | trunc 63 -}}
{{- end -}}

{{- define "crdInstallAnnotations" -}}
"helm.sh/hook": "pre-install,pre-upgrade"
"helm.sh/hook-delete-policy": "before-hook-creation,hook-succeeded,hook-failed"
{{- end -}}

{{/* Create a label which can be used to select any orphaned crd-install hook resources */}}
{{- define "crdInstallSelector" -}}
{{- printf "%s" "crd-install-hook" -}}
{{- end -}}

{{/* Usage:
    {{ include "controllerVolumeName" (merge (dict "volumeName" "hello") .) | quote }}
*/}}
{{- define "controllerVolumeName" -}}
{{- printf "%s-controller-%s-volume" (include "name" .) .volumeName -}}
{{- end -}}

{{- define "appPlatform.twoStepInstall" -}}
{{- $is_chart_operator := lookup "application.giantswarm.io/v1alpha1" "Chart" "giantswarm" "chart-operator" -}}
{{- $is_chart_operator_bad := false }}
{{- if $is_chart_operator }}
{{- $is_chart_operator_bad = (semverCompare "< 2.26.0-0" $is_chart_operator.spec.version) }}
{{- end }}

{{- $is_this_chart_cr := lookup "application.giantswarm.io/v1alpha1" "Chart" "giantswarm" . -}}
{{- $is_outside_app_platform := false }}
{{- if $is_this_chart_cr }}
{{- $is_outside_app_platform = true }}
{{- end }}

{{- if and $is_chart_operator_bad $is_outside_app_platform }}
{{- print "unsupported: true" -}}
{{- else -}}
{{- print "unsupported: false" -}}
{{- end -}}
{{- end -}}
