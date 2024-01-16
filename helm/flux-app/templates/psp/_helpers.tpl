{{- define "pspName" -}}
{{ printf "%s-pvc-psp" (include "name" .)}}
{{- end }}

{{- define "pspNameFinal" }}
{{- if .Values.namePostfix }}
{{- printf "%s-%s" (include "pspName" .) .Values.namePostfix }}
{{ else }}
{{- include "pspName" . }}
{{ end }}
{{- end -}}

