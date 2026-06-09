# TelemetryFlow-Viz Product Overview

TelemetryFlow-Viz is a standalone observability dashboard for visualizing Metrics, Logs, Traces, and Exemplars. It provides a modern, real-time interface for monitoring and analyzing telemetry data from distributed systems.

## Core Features

- **Metrics Explorer**: Query and visualize metrics with interactive time series charts
- **Log Viewer**: Real-time log streaming with advanced filtering and search capabilities
- **Trace Viewer**: Distributed tracing with waterfall, flame graph, and node graph visualizations
- **Exemplars**: Metric-to-trace correlation for deep-dive analysis
- **Dashboard Builder**: Create custom dashboards with drag-and-drop widgets
- **Alerting**: Configure and manage alert rules with templates
- **Correlation Engine**: Cross-signal correlation for root cause analysis

## Chart Features

- **Multiple chart types**: Toggle between Line, Area, and Bar charts on all visualizations
- **Interactive data points**: Hover and click interactions on line/area charts
- **Zoom functionality**: Expand any chart to full-screen modal view
- **Chart synchronization**: Linked zooming across related charts in the same group
- **Dark/Light mode**: Full theme support with automatic system detection

## Trace Analysis Capabilities

- **Waterfall View**: Hierarchical span timeline with service breakdown and latency analysis
- **Flame Graph**: Aggregated latency visualization for performance bottlenecks
- **Node Graph**: Service dependency topology with multiple layout algorithms
- **Related Logs**: Automatically correlated logs for each trace
- **Span Details**: Detailed attributes, events, links, and metadata

## Technology Stack

- **Framework**: Vue 3 with Composition API
- **Language**: TypeScript 5.x with strict type checking
- **Build Tool**: Vite 6.x with fast HMR
- **State Management**: Pinia for reactive stores
- **UI Library**: Naive UI for component library
- **Styling**: UnoCSS for atomic CSS with SCSS for custom styles
- **Charts**: ECharts 5.x with vue-echarts wrapper
- **Real-time**: Socket.IO client for WebSocket streaming
- **Package Manager**: pnpm 9.x

## Architecture

The application follows a modular Vue 3 architecture:

- **Views**: Page-level components organized by feature
- **Components**: Reusable UI components (charts, common, feature-specific)
- **Composables**: Vue composition hooks for shared logic
- **Store**: Pinia stores for state management
- **API**: Axios-based API clients for TFO-Collector
- **Mocks**: Comprehensive mock data generators for development

## Data Source Integration

TelemetryFlow-Viz connects to **TFO-Collector** (TelemetryFlow Collector) which provides:

- HTTP/JSON API for querying telemetry data
- gRPC endpoints for high-performance data ingestion
- WebSocket streaming for real-time updates
- OTLP-compatible ingestion endpoints

## Default Access

Basic authentication with configurable credentials:

- **Username**: `admin` (configurable via `TELEMETRYFLOW_VIZ_ADMIN`)
- **Password**: `Admin@654123` (configurable via `TELEMETRYFLOW_VIZ_PASSWORD`)

> **Production Note**: Change default credentials via environment variables or deploy behind a reverse proxy with proper authentication.

## Deployment Options

- **Development**: Local development server with hot reload
- **Docker**: Containerized deployment with Nginx
- **Demo**: Production demo with Nginx + Let's Encrypt SSL
- **Mock Mode**: Standalone mode with mock data (no backend required)
