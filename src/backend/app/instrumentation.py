# Módulo de configuração do OpenTelemetry
import os
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# Instrumentadores automáticos
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

def setup_opentelemetry(app):
    """Configura o OpenTelemetry para a aplicação Fintelli."""
    
    # Obtém o nome do serviço do ambiente, default para 'unknown_service'
    service_name = os.environ.get("OTEL_SERVICE_NAME", "fintelli-backend")
    resource = Resource(attributes={"service.name": service_name})

    # --- Configuração de Traces ---
    tracer_provider = TracerProvider(resource=resource)
    trace_exporter = OTLPSpanExporter() # Usa o endpoint da variável de ambiente
    tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    trace.set_tracer_provider(tracer_provider)

    # --- Configuração de Métricas ---
    metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # Instrumenta as bibliotecas
    FastAPIInstrumentor.instrument_app(app)
    Psycopg2Instrumentor().instrument()
    RedisInstrumentor().instrument()

    print(f"OpenTelemetry configurado para o serviço: {service_name}")

# --- Métricas Customizadas ---
# É uma boa prática criar um "medidor" para seu módulo
meter = metrics.get_meter("fintelli.api.meter")

transactions_created_counter = meter.create_counter(
    name="transactions_created_total",
    description="Conta o número total de transações criadas",
    unit="1",
)
