{{/*
Define o nome completo do chart.
*/}}
{{- define "finance-stack.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Define o nome para o backend.
*/}}
{{- define "finance-stack.backend.name" -}}
{{- printf "%s-backend" (include "finance-stack.fullname" .) }}
{{- end }}

{{/*
Define o nome para o frontend.
*/}}
{{- define "finance-stack.frontend.name" -}}
{{- printf "%s-frontend" (include "finance-stack.fullname" .) }}
{{- end }}

{{/*
Define o nome para o otel-collector.
*/}}
{{- define "finance-stack.otel-collector.name" -}}
{{- printf "%s-otel-collector" (include "finance-stack.fullname" .) }}
{{- end }}
