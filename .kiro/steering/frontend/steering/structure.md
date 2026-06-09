# Project Structure & Organization

## Root Directory Structure

```
telemetryflow-viz/
├── src/                    # Source code (TypeScript + Vue)
├── public/                 # Static assets (favicons, images)
├── config/                 # Nginx and SSL configurations
├── docker/                 # Docker-specific configurations
├── docs/                   # Documentation and API specs
├── scripts/                # Utility scripts
├── dist/                   # Production build output
├── build/                  # Build artifacts
└── node_modules/           # Dependencies (managed by pnpm)
```

## Source Code Architecture (src/)

The codebase follows a modular Vue 3 architecture with feature-based organization:

```
src/
├── main.ts                 # Application entry point
├── App.vue                 # Root Vue component
│
├── api/                    # API clients for TFO-Collector
│   ├── index.ts            # API configuration and exports
│   ├── collector.ts        # Collector API client
│   ├── metrics.ts          # Metrics API endpoints
│   ├── logs.ts             # Logs API endpoints
│   ├── traces.ts           # Traces API endpoints
│   ├── exemplars.ts        # Exemplars API endpoints
│   └── kubernetes.ts       # Kubernetes monitoring API
│
├── components/             # Reusable Vue components
│   ├── charts/             # Chart components
│   │   ├── TimeSeriesChart.vue
│   │   ├── BarChart.vue
│   │   ├── ScatterChart.vue
│   │   ├── HeatmapChart.vue
│   │   ├── GaugeChart.vue
│   │   ├── ChartCard.vue
│   │   ├── MiniChartCard.vue
│   │   ├── ChartTypeToggle.vue
│   │   ├── ChartZoomModal.vue
│   │   ├── StatPanel.vue
│   │   └── index.ts
│   ├── common/             # Common UI components
│   │   ├── DataTable.vue
│   │   ├── DataTableCard.vue
│   │   ├── EmptyState.vue
│   │   ├── LoadingSpinner.vue
│   │   ├── StatCard.vue
│   │   ├── StatsBar.vue
│   │   └── index.ts
│   ├── alerts/             # Alert-related components
│   ├── dashboard/          # Dashboard builder components
│   ├── exemplars/          # Exemplar components
│   ├── metrics/            # Metrics explorer components
│   └── traces/             # Trace viewer components
│
├── composables/            # Vue composition hooks
│   ├── index.ts
│   ├── useChartGroup.ts    # Chart synchronization
│   ├── useChartZoom.ts     # Chart zoom functionality
│   └── useK8sMockData.ts   # Kubernetes mock data
│
├── config/                 # Application configuration
│   ├── index.ts            # Main config exports
│   ├── collector.ts        # Collector connection config
│   └── theme.ts            # Theme configuration
│
├── layouts/                # Layout components
│   └── ...                 # Main layout, auth layout, etc.
│
├── mocks/                  # Mock data generators
│   ├── index.ts            # Unified exports
│   ├── shared.ts           # Shared utilities and constants
│   ├── metrics.ts          # Metrics mock data
│   ├── logs.ts             # Logs mock data
│   ├── traces.ts           # Traces mock data
│   ├── exemplars.ts        # Exemplars mock data
│   ├── correlations.ts     # Correlation mock data
│   ├── home.ts             # Home dashboard mock data
│   ├── alerts.ts           # Alerts mock data
│   ├── kubernetes.ts       # Kubernetes mock data
│   └── data/               # Static mock data
│       ├── realistic-data.json
│       ├── correlated-registry.ts
│       └── static-generator.ts
│
├── router/                 # Vue Router configuration
│   └── index.ts            # Route definitions
│
├── services/               # Business logic services
│   ├── index.ts
│   └── mockDataGenerator.ts # Mock data service
│
├── store/                  # Pinia stores
│   ├── index.ts            # Store exports
│   ├── app.ts              # App-wide state
│   ├── auth.ts             # Authentication state
│   ├── dashboard.ts        # Dashboard state
│   ├── metrics.ts          # Metrics state
│   ├── logs.ts             # Logs state
│   ├── traces.ts           # Traces state
│   ├── exemplars.ts        # Exemplars state
│   ├── alerts.ts           # Alerts state
│   └── kubernetes.ts       # Kubernetes state
│
├── streaming/              # WebSocket/streaming
│   ├── index.ts
│   ├── websocket.ts        # WebSocket client
│   └── handlers.ts         # Stream event handlers
│
├── styles/                 # Global styles
│   ├── global.scss         # Global styles and utilities
│   ├── variables.scss      # SCSS variables
│   ├── reset.css           # CSS reset
│   └── transitions.css     # Transition animations
│
├── types/                  # TypeScript type definitions
│   ├── index.ts            # Type exports
│   ├── api.ts              # API types
│   ├── dashboard.ts        # Dashboard types
│   ├── metric.ts           # Metric types
│   ├── log.ts              # Log types
│   ├── trace.ts            # Trace types
│   ├── exemplar.ts         # Exemplar types
│   ├── auto-imports.d.ts   # Auto-generated imports
│   └── components.d.ts     # Auto-generated components
│
├── utils/                  # Utility functions
│   ├── index.ts
│   ├── format.ts           # Formatting utilities
│   ├── stats.ts            # Statistical calculations
│   ├── datatable.ts        # DataTable utilities
│   ├── export.ts           # Export utilities
│   ├── clipboard.ts        # Clipboard utilities
│   ├── json.ts             # JSON utilities
│   └── constants.ts        # Constants
│
└── views/                  # Page components
    ├── home/               # Home dashboard
    │   └── index.vue
    ├── auth/               # Authentication pages
    │   └── login.vue
    ├── telemetry/          # Telemetry pages
    │   ├── metrics/
    │   │   ├── index.vue
    │   │   └── detail.vue
    │   ├── logs/
    │   │   ├── index.vue
    │   │   └── detail.vue
    │   ├── traces/
    │   │   ├── index.vue
    │   │   ├── detail.vue
    │   │   └── features/
    │   │       ├── TraceFilterSidebar.vue
    │   │       ├── TraceListItem.vue
    │   │       ├── TraceMonitorTab.vue
    │   │       ├── TraceNodeGraph.vue
    │   │       └── index.ts
    │   ├── exemplars/
    │   │   └── index.vue
    │   └── correlations/
    │       └── index.vue
    ├── monitoring/         # Monitoring pages
    │   └── kubernetes/
    │       ├── overview.vue
    │       ├── nodes.vue
    │       ├── pods.vue
    │       ├── deployment.vue
    │       ├── namespace.vue
    │       ├── pv.vue
    │       └── *-features/ # Feature-specific components
    ├── dashboards/         # Dashboard pages
    │   ├── index.vue
    │   ├── view.vue
    │   └── builder.vue
    ├── alerts/             # Alert pages
    │   ├── index.vue
    │   └── rules.vue
    ├── settings/           # Settings pages
    │   └── index.vue
    └── error/              # Error pages
        ├── ErrorPage.vue
        ├── 401.vue
        ├── 403.vue
        ├── 404.vue
        ├── 500.vue
        ├── 502.vue
        ├── 503.vue
        └── 504.vue
```

## Configuration Structure (config/)

Service configurations for deployment:

```
config/
├── nginx/                  # Nginx configuration
│   ├── nginx.conf          # Main Nginx config
│   └── conf.d/
│       ├── default.conf    # SSL server config
│       ├── default.conf.init # HTTP-only config
│       └── local.conf      # Local development config
├── certbot/                # Let's Encrypt configuration
│   └── cli.ini             # Certbot CLI settings
└── init-ssl.sh             # SSL initialization script
```

## Naming Conventions

### Files and Directories

#### Vue Components

- **Single File Components**: PascalCase (e.g., `TimeSeriesChart.vue`, `DataTable.vue`)
- **Page Components**: kebab-case (e.g., `index.vue`, `detail.vue`)
- **Feature Components**: PascalCase with descriptive names (e.g., `TraceFilterSidebar.vue`)

#### TypeScript Files

- **Composables**: camelCase with `use` prefix (e.g., `useChartGroup.ts`)
- **Stores**: kebab-case (e.g., `metrics.ts`, `traces.ts`)
- **Types**: kebab-case (e.g., `metric.ts`, `trace.ts`)
- **Utils**: kebab-case (e.g., `format.ts`, `stats.ts`)
- **API Clients**: kebab-case (e.g., `metrics.ts`, `logs.ts`)

#### Styles

- **Global Styles**: kebab-case (e.g., `global.scss`, `variables.scss`)
- **Component Styles**: Scoped within `.vue` files or separate `.scss` files

### Code Conventions

#### Vue Components

- **Component Names**: PascalCase in script, kebab-case in templates
- **Props**: camelCase in script, kebab-case in templates
- **Events**: kebab-case (e.g., `@update:value`, `@chart-zoom`)
- **Composables**: camelCase with `use` prefix (e.g., `useChartGroup()`)

#### TypeScript

- **Interfaces**: PascalCase with `I` prefix optional (e.g., `Metric`, `IMetric`)
- **Types**: PascalCase (e.g., `MetricType`, `ChartOptions`)
- **Enums**: PascalCase (e.g., `ChartType`, `LogLevel`)
- **Constants**: SCREAMING_SNAKE_CASE (e.g., `DEFAULT_REFRESH_INTERVAL`)

## Mock Data Structure

The mock data system is modular and feature-based:

```
src/mocks/
├── index.ts                # Unified exports
├── shared.ts               # Shared utilities
│   ├── SERVICES            # Service names array
│   ├── OPERATIONS          # Operation names array
│   ├── LATENCY_BUCKETS     # Latency histogram buckets
│   └── Helper functions    # Random generators, formatters
├── metrics.ts              # Metrics mock data
│   ├── generateMetricNames()
│   ├── generateMetricMetadata()
│   ├── generateMetricTimeSeries()
│   └── metricsMock object
├── logs.ts                 # Logs mock data
│   ├── generateLogs()
│   ├── generateLogVolume()
│   └── logsMock object
├── traces.ts               # Traces mock data
│   ├── generateTraces()
│   ├── generateTraceSpans()
│   ├── generateFlameGraph()
│   └── tracesMock object
├── exemplars.ts            # Exemplars mock data
├── correlations.ts         # Correlation mock data
├── home.ts                 # Home dashboard mock data
├── alerts.ts               # Alerts mock data
└── kubernetes.ts           # Kubernetes mock data
```

## Route Structure

```
/                           # Home dashboard
/login                      # Login page
/metrics                    # Metrics explorer
/metrics/:id                # Metric detail
/logs                       # Log viewer
/logs/:id                   # Log detail
/traces                     # Trace list
/traces/:id                 # Trace detail (waterfall, flame, node graph)
/exemplars                  # Exemplars view
/correlations               # Cross-signal correlation
/dashboards                 # Dashboard list
/dashboards/:id             # Dashboard view
/dashboards/builder         # Dashboard builder
/alerts                     # Alert list
/alerts/rules               # Alert rules
/monitoring/kubernetes/*    # Kubernetes monitoring pages
/settings                   # Settings
/error/*                    # Error pages
```

## Import Path Conventions

- **Absolute imports**: Use `@/` for `src/` directory (e.g., `@/components/charts`)
- **Relative imports**: Use `./` or `../` for nearby files
- **Barrel exports**: Use `index.ts` files for clean imports
- **Auto imports**: Vue APIs, composables, and stores are auto-imported

### Examples

```typescript
// Absolute imports (preferred)
import { TimeSeriesChart } from "@/components/charts";
import { useMetricsStore } from "@/store/metrics";
import type { Metric } from "@/types/metric";

// Relative imports (for nearby files)
import { formatDuration } from "./utils";
import TraceSpan from "./TraceSpan.vue";

// Auto-imported (no import needed)
const route = useRoute();
const router = useRouter();
const metricsStore = useMetricsStore();
```

## Component Organization

### Feature-based Components

Components are organized by feature with a `features/` subdirectory for complex views:

```
views/telemetry/traces/
├── index.vue               # Main trace list page
├── detail.vue              # Trace detail page
└── features/               # Trace-specific components
    ├── TraceFilterSidebar.vue
    ├── TraceListItem.vue
    ├── TraceMonitorTab.vue
    ├── TraceNodeGraph.vue
    └── index.ts            # Barrel export
```

### Shared Components

Reusable components are organized by category:

```
components/
├── charts/                 # Chart components (reusable across features)
├── common/                 # Common UI components (tables, cards, etc.)
├── alerts/                 # Alert-specific components
├── dashboard/              # Dashboard-specific components
├── exemplars/              # Exemplar-specific components
├── metrics/                # Metrics-specific components
└── traces/                 # Trace-specific components
```

## Environment-Specific Files

- **Development**: `.env.development` (local dev configuration)
- **Production**: `.env.production` (production configuration)
- **Examples**: `.env.development.example`, `.env.production.example`
- **Docker**: Environment variables in `docker-compose.yml` files
- **Vite**: Environment variables accessed via `import.meta.env`

## Build Output Structure

```
dist/
├── assets/
│   ├── index-[hash].js     # Main bundle
│   ├── vue-vendor-[hash].js # Vue dependencies
│   ├── ui-vendor-[hash].js  # UI library
│   ├── chart-vendor-[hash].js # Chart library
│   ├── index-[hash].css    # Compiled styles
│   └── [asset]-[hash].*    # Other assets
├── index.html              # Entry HTML
├── favicon.png
├── favicon.svg
└── user.svg
```

## Documentation Structure

```
docs/
├── README.md               # Main documentation
├── api-reference.md        # API documentation
├── architecture.md         # Architecture overview
├── components.md           # Component documentation
├── configuration.md        # Configuration guide
├── deployment.md           # Deployment guide
├── development.md          # Development guide
├── dfd.md                  # Data flow diagrams
├── erd.md                  # Entity relationship diagrams
├── faq.md                  # Frequently asked questions
├── getting-started.md      # Getting started guide
├── mock-server.md          # Mock server documentation
├── openapi.yaml            # OpenAPI specification
├── overview.md             # Project overview
└── troubleshooting.md      # Troubleshooting guide
```

This structure ensures a clean, maintainable, and scalable Vue 3 application with clear separation of concerns and feature-based organization.
