---
description: 'Observability guidance for Agent Framework using OpenTelemetry GenAI Semantic Conventions.'
applyTo: '**/*.py'
---

# Observability Instructions

Observability is essential for building reliable, maintainable agent systems. Agent Framework provides built-in OpenTelemetry support for tracing, logging, and metrics following the [OpenTelemetry GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/).

When generating code, reviewing changes, or answering questions related to observability in Agent Framework projects, follow the guidance below.

## OpenTelemetry Integration

Agent Framework emits traces, logs, and metrics via OpenTelemetry.

### Default Packages (installed with Agent Framework)
- `opentelemetry-api`
- `opentelemetry-sdk`
- `opentelemetry-semantic-conventions-ai`

### Exporters (install as needed — not bundled by default)
- gRPC: `opentelemetry-exporter-otlp-proto-grpc`
- HTTP: `opentelemetry-exporter-otlp-proto-http`
- Azure Application Insights: `azure-monitor-opentelemetry`

Use the [OpenTelemetry Registry](https://opentelemetry.io/ecosystem/registry/) to find additional exporters and instrumentation packages.

## Five Patterns for Configuring Observability (Python)

### 1. Standard OpenTelemetry environment variables (Recommended)

Configure everything via environment variables:

```python
from agent_framework.observability import configure_otel_providers

# Reads OTEL_EXPORTER_OTLP_* environment variables automatically
configure_otel_providers()
```

For console-only output:

```bash
ENABLE_CONSOLE_EXPORTERS=true
```

```python
from agent_framework.observability import configure_otel_providers
configure_otel_providers()
```

### 2. Custom Exporters

```python
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from agent_framework.observability import configure_otel_providers

exporters = [
    OTLPSpanExporter(endpoint="http://localhost:4317", compression=Compression.Gzip),
    OTLPLogExporter(endpoint="http://localhost:4317"),
    OTLPMetricExporter(endpoint="http://localhost:4317"),
]

configure_otel_providers(exporters=exporters, enable_sensitive_data=True)
```

### 3. Third-party setup

Run the third-party setup first, then call `enable_instrumentation()` to activate Agent Framework code paths.

Azure Monitor:

```python
from azure.monitor.opentelemetry import configure_azure_monitor
from agent_framework.observability import create_resource, enable_instrumentation

configure_azure_monitor(
    connection_string="InstrumentationKey=...",
    resource=create_resource(),
    enable_live_metrics=True,
)
enable_instrumentation(enable_sensitive_data=False)
```

Langfuse:

```python
from agent_framework.observability import enable_instrumentation
from langfuse import get_client

langfuse = get_client()
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")

enable_instrumentation(enable_sensitive_data=False)
```

### 4. Manual setup

Set up exporters, providers, and instrumentation manually. Use `create_resource()` to build a resource with the correct service name/version. See the [OpenTelemetry Python documentation](https://opentelemetry.io/docs/languages/python/) for details.

### 5. Auto-instrumentation (zero-code)

```bash
opentelemetry-instrument \
    --traces_exporter console,otlp \
    --metrics_exporter console \
    --service_name your-service-name \
    --exporter_otlp_endpoint 0.0.0.0:4317 \
    python agent_framework_app.py
```

## Custom Tracers and Meters

```python
from agent_framework.observability import get_tracer, get_meter

tracer = get_tracer()
meter = get_meter()

with tracer.start_as_current_span("my_custom_span"):
    pass

counter = meter.create_counter("my_custom_counter")
counter.add(1, {"key": "value"})
```

These wrappers return a tracer/meter from the global provider with `agent_framework` set as the instrumentation library name.

## Environment Variables

### Agent Framework
- `ENABLE_INSTRUMENTATION` — enable OpenTelemetry instrumentation (default: `false`).
- `ENABLE_SENSITIVE_DATA` — enable logging of prompts, responses, function arguments, and results (default: `false`). **Do not enable in production.**
- `ENABLE_CONSOLE_EXPORTERS` — enable console output for telemetry (default: `false`).
- `VS_CODE_EXTENSION_PORT` — port for AI Toolkit / Microsoft Foundry VS Code extension integration.

> **Warning:** Sensitive data includes prompts and responses. Only enable `ENABLE_SENSITIVE_DATA` in development or test environments.

### Standard OpenTelemetry

OTLP configuration:
- `OTEL_EXPORTER_OTLP_ENDPOINT` — base endpoint for all signals (e.g., `http://localhost:4317`)
- `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` — traces-specific override
- `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` — metrics-specific override
- `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT` — logs-specific override
- `OTEL_EXPORTER_OTLP_PROTOCOL` — `grpc` (default) or `http`
- `OTEL_EXPORTER_OTLP_HEADERS` — comma-separated headers (e.g., `key1=value1,key2=value2`)

Service identification:
- `OTEL_SERVICE_NAME` (default: `agent_framework`)
- `OTEL_SERVICE_VERSION` (default: package version)
- `OTEL_RESOURCE_ATTRIBUTES`

## Microsoft Foundry Setup

Install:

```bash
pip install azure-monitor-opentelemetry
```

For Foundry projects, configure observability directly from the `FoundryChatClient`:

```python
import os
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import AzureCliCredential

async def main():
    async with AzureCliCredential() as credential:
        client = FoundryChatClient(
            project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
            model=os.environ["FOUNDRY_MODEL"],
            credential=credential,
        )
        await client.configure_azure_monitor(enable_live_metrics=True)
```

For non-Foundry projects with Application Insights, register a custom agent in Foundry and run with the matching OpenTelemetry agent ID:

```python
from azure.monitor.opentelemetry import configure_azure_monitor
from agent_framework.observability import create_resource, enable_instrumentation

configure_azure_monitor(
    connection_string="InstrumentationKey=...",
    resource=create_resource(),
    enable_live_metrics=True,
)
enable_instrumentation()

agent = Agent(
    client=...,
    name="My Agent",
    instructions="You are a helpful assistant.",
    id="<OpenTelemetry agent ID>",
)
```

## Aspire Dashboard (Local Development)

Run the dashboard locally via Docker:

```bash
docker run --rm -it -d \
    -p 18888:18888 \
    -p 4317:18889 \
    --name aspire-dashboard \
    mcr.microsoft.com/dotnet/aspire-dashboard:latest
```

- Web UI: `http://localhost:18888`
- OTLP endpoint: `http://localhost:4317`

Configure your application:

```bash
ENABLE_INSTRUMENTATION=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

> Agent Framework does **not** auto-load `.env` files — call `load_dotenv()` at application startup if you use one.

## Spans and Metrics

### Spans (auto-created)
- `invoke_agent <agent_name>` — top-level span for each agent invocation; parents all child spans.
- `chat <model_name>` — created when the agent calls the chat model. Includes prompt/response attributes when `enable_sensitive_data=True`.
- `execute_tool <function_name>` — created when the agent calls a function tool. Includes arguments/result attributes when `enable_sensitive_data=True`.

### Metrics
Chat client / chat operations:
- `gen_ai.client.operation.duration` (histogram, seconds)
- `gen_ai.client.token.usage` (histogram, tokens)

Function invocation:
- `agent_framework.function.invocation.duration` (histogram, seconds)

### Example trace output

```json
{
    "name": "invoke_agent Joker",
    "context": {
        "trace_id": "0xf2258b51421fe9cf4c0bd428c87b1ae4",
        "span_id": "0x2cad6fc139dcf01d",
        "trace_state": "[]"
    },
    "kind": "SpanKind.CLIENT",
    "parent_id": null,
    "start_time": "2025-09-25T11:00:48.663688Z",
    "end_time": "2025-09-25T11:00:57.271389Z",
    "status": { "status_code": "UNSET" },
    "attributes": {
        "gen_ai.operation.name": "invoke_agent",
        "gen_ai.system": "openai",
        "gen_ai.agent.id": "Joker",
        "gen_ai.agent.name": "Joker",
        "gen_ai.request.instructions": "You are good at telling jokes.",
        "gen_ai.response.id": "chatcmpl-CH6fgKwMRGDtGNO3H88gA3AG2o7c5",
        "gen_ai.usage.input_tokens": 26,
        "gen_ai.usage.output_tokens": 29
    }
}
```

## Complete Example

```python
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework import Agent, tool
from agent_framework.observability import configure_otel_providers, get_tracer
from agent_framework.openai import OpenAIChatClient
from opentelemetry.trace import SpanKind
from opentelemetry.trace.span import format_trace_id
from pydantic import Field


# NOTE: approval_mode="never_require" is for sample brevity. Use "always_require" in production.
@tool(approval_mode="never_require")
async def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    await asyncio.sleep(randint(0, 10) / 10.0)
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def main():
    configure_otel_providers()

    questions = [
        "What's the weather in Amsterdam?",
        "and in Paris, and which is better?",
        "Why is the sky blue?",
    ]

    with get_tracer().start_as_current_span("Scenario: Agent Chat", kind=SpanKind.CLIENT) as current_span:
        print(f"Trace ID: {format_trace_id(current_span.get_span_context().trace_id)}")

        agent = Agent(
            client=OpenAIChatClient(),
            tools=get_weather,
            name="WeatherAgent",
            instructions="You are a weather assistant.",
            id="weather-agent",
        )
        thread = agent.create_session()
        for question in questions:
            print(f"\nUser: {question}")
            print(f"{agent.name}: ", end="")
            async for update in agent.run(question, session=thread, stream=True):
                if update.text:
                    print(update.text, end="")


if __name__ == "__main__":
    asyncio.run(main())
```

## Review Guidelines

When reviewing or generating observability code:
- Prefer pattern #1 (environment variables) for new code unless a specific need dictates otherwise.
- Never enable `ENABLE_SENSITIVE_DATA` in production code paths or commit it as `true` in shared `.env` files.
- Confirm exporters are explicitly installed — they are not bundled with Agent Framework.
- Ensure `create_resource()` is used when integrating with third-party setups (Azure Monitor, Langfuse) to preserve service identification.
- Validate that custom spans/meters use `get_tracer()` / `get_meter()` from `agent_framework.observability` rather than constructing providers directly.
- For Foundry, prefer `FoundryChatClient.configure_azure_monitor()` over manual Azure Monitor setup.
- Reference the observability samples in the `microsoft/agent-framework` repository for working examples.
