// Instrumentação OpenTelemetry para o Frontend

// Importa os módulos necessários de um CDN
// Em um projeto real, você usaria um bundler como Webpack/Vite
import { WebTracerProvider } from 'https://cdn.jsdelivr.net/npm/@opentelemetry/sdk-trace-web@1.17.0/build/src/WebTracerProvider.js';
import { SimpleSpanProcessor } from 'https://cdn.jsdelivr.net/npm/@opentelemetry/sdk-trace-base@1.17.0/build/src/SimpleSpanProcessor.js';
import { OTLPTraceExporter } from 'https://cdn.jsdelivr.net/npm/@opentelemetry/exporter-trace-otlp-http@0.43.0/build/src/platform/browser/OTLPTraceExporter.js';
import { registerInstrumentations } from 'https://cdn.jsdelivr.net/npm/@opentelemetry/instrumentation@0.43.0/build/src/platform/browser/instrumentation.js';
import { FetchInstrumentation } from 'https://cdn.jsdelivr.net/npm/@opentelemetry/instrumentation-fetch@0.43.0/build/src/fetch.js';
import { ZoneContextManager } from 'https://cdn.jsdelivr.net/npm/@opentelemetry/context-zone@1.17.0/build/src/ZoneContextManager.js';
import { Resource } from 'https://cdn.jsdelivr.net/npm/@opentelemetry/resources@1.17.0/build/src/Resource.js';
import { SemanticResourceAttributes } from 'https://cdn.jsdelivr.net/npm/@opentelemetry/semantic-conventions@1.17.0/build/src/enums/SemanticResourceAttributes.js';

function setupFrontendTelemetry() {
    // Define o recurso (nome do serviço)
    const resource = new Resource({
        [SemanticResourceAttributes.SERVICE_NAME]: 'finance-frontend',
    });

    // Cria um provedor de traces
    const provider = new WebTracerProvider({
        resource: resource,
    });

    // Configura o exportador para enviar traces via HTTP para o nosso Collector
    // O Nginx atuará como proxy para o endpoint /v1/traces
    const exporter = new OTLPTraceExporter({
        url: '/v1/traces', // O Nginx irá redirecionar isso para http://otel-collector:4318/v1/traces
    });

    // Adiciona um processador de spans ao provedor
    provider.addSpanProcessor(new SimpleSpanProcessor(exporter));

    // Define o provedor como o provedor global
    provider.register({
        contextManager: new ZoneContextManager(),
    });

    // Registra a instrumentação automática para a API Fetch
    registerInstrumentations({
        instrumentations: [
            new FetchInstrumentation({
                // Propaga o contexto de trace nos cabeçalhos das requisições
                propagateTraceHeaderCorsUrls: [
                    /.+/g, // Propaga para todas as URLs
                ],
            }),
        ],
    });

    console.log('OpenTelemetry for Frontend configurado.');
}

// Executa a configuração
setupFrontendTelemetry();

