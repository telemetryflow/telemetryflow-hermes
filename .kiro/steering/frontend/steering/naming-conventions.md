# Naming Conventions for TelemetryFlow-Viz

This document defines consistent naming patterns for the Vue.js visualization dashboard.

## Core Principles

1. **Consistency**: Same pattern across all files and code
2. **Clarity**: Names reveal purpose and type
3. **TypeScript/Vue**: Follow Vue 3 and TypeScript conventions
4. **Searchability**: Easy to find files with grep/search
5. **Modern Standards**: Follow current Vue 3 ecosystem best practices

## File Naming Conventions

### Vue Components

| Type                    | Pattern    | Example                   | ❌ Wrong                       |
| ----------------------- | ---------- | ------------------------- | ------------------------------ |
| **Reusable Components** | PascalCase | `TimeSeriesChart.vue`     | ~~`time-series-chart.vue`~~    |
| **Page Components**     | kebab-case | `index.vue`, `detail.vue` | ~~`Index.vue`~~                |
| **Feature Components**  | PascalCase | `TraceFilterSidebar.vue`  | ~~`trace-filter-sidebar.vue`~~ |
| **Layout Components**   | PascalCase | `MainLayout.vue`          | ~~`main-layout.vue`~~          |

**Rules**:

- ✅ Multi-word component names (avoid single words like `Chart.vue`)
- ✅ PascalCase for reusable components
- ✅ kebab-case for page-level components (index, detail)
- ✅ Descriptive names that indicate purpose

### TypeScript Files

| Type            | Pattern                     | Example                    | ❌ Wrong                     |
| --------------- | --------------------------- | -------------------------- | ---------------------------- |
| **Composables** | camelCase with `use` prefix | `useChartGroup.ts`         | ~~`chart-group.ts`~~         |
| **Stores**      | kebab-case                  | `metrics.ts`, `traces.ts`  | ~~`MetricsStore.ts`~~        |
| **Types**       | kebab-case                  | `metric.ts`, `trace.ts`    | ~~`Metric.ts`~~              |
| **Utils**       | kebab-case                  | `format.ts`, `stats.ts`    | ~~`Format.ts`~~              |
| **API Clients** | kebab-case                  | `metrics.ts`, `logs.ts`    | ~~`metricsApi.ts`~~          |
| **Services**    | camelCase                   | `mockDataGenerator.ts`     | ~~`mock-data-generator.ts`~~ |
| **Config**      | kebab-case                  | `collector.ts`, `theme.ts` | ~~`Collector.ts`~~           |

### Style Files

| Type                 | Pattern                                           | Example                         |
| -------------------- | ------------------------------------------------- | ------------------------------- |
| **Global Styles**    | kebab-case                                        | `global.scss`, `variables.scss` |
| **Component Styles** | Scoped in `.vue` files or matching component name |

### Mock Data Files

| Type                 | Pattern    | Example                                    |
| -------------------- | ---------- | ------------------------------------------ |
| **Mock Modules**     | kebab-case | `metrics.ts`, `traces.ts`, `kubernetes.ts` |
| **Shared Utilities** | kebab-case | `shared.ts`                                |
| **Static Data**      | kebab-case | `realistic-data.json`                      |

## Code Naming Conventions

### Vue Components

```vue
<script setup lang="ts">
// Component name (PascalCase in script)
// Used as: <TimeSeriesChart />

// Props interface (PascalCase)
interface Props {
  metricId: string; // camelCase
  showLegend?: boolean; // camelCase
}

// Emits (kebab-case in template, camelCase in type)
const emit = defineEmits<{
  "update:value": [value: number]; // kebab-case
  "chart-zoom": [range: object]; // kebab-case
}>();

// Reactive state (camelCase)
const isLoading = ref(false);
const chartData = ref<Metric[]>([]);

// Computed properties (camelCase)
const filteredData = computed(() => {
  return chartData.value.filter((m) => m.value > 0);
});

// Methods (camelCase)
const fetchData = async () => {
  // Implementation
};

const handleChartZoom = (range: ZoomRange) => {
  emit("chart-zoom", range);
};
</script>

<template>
  <!-- Component usage: kebab-case -->
  <div class="time-series-chart">
    <loading-spinner v-if="isLoading" />

    <!-- Props: kebab-case -->
    <chart-component
      :metric-id="metricId"
      :show-legend="showLegend"
      @chart-zoom="handleChartZoom"
    />
  </div>
</template>

<style scoped lang="scss">
/* CSS classes: kebab-case */
.time-series-chart {
  /* Styles */
}

.chart-container {
  /* Styles */
}
</style>
```

### TypeScript Interfaces and Types

```typescript
// Interfaces: PascalCase
export interface Metric {
  id: string;
  name: string;
  value: number;
  timestamp: number;
  labels: Record<string, string>;
}

// Type aliases: PascalCase
export type MetricTimeSeries = Array<{
  timestamp: number;
  value: number;
}>;

// Enums: PascalCase for enum, SCREAMING_SNAKE_CASE for values
export enum ChartType {
  LINE = "LINE",
  BAR = "BAR",
  AREA = "AREA",
}

// Union types: PascalCase
export type LogLevel = "debug" | "info" | "warn" | "error";
```

### Composables

```typescript
// composables/useChartGroup.ts

// Function name: camelCase with 'use' prefix
export function useChartGroup(options: ChartGroupOptions) {
  // Internal state: camelCase
  const chartInstance = ref<any>(null);
  const zoomRange = ref<ZoomRange | null>(null);

  // Methods: camelCase
  const registerChart = (instance: any) => {
    chartInstance.value = instance;
  };

  const syncZoom = (range: ZoomRange) => {
    zoomRange.value = range;
  };

  return {
    chartInstance,
    zoomRange,
    registerChart,
    syncZoom,
  };
}
```

### Pinia Stores

```typescript
// store/metrics.ts

// Store name: camelCase with 'use' prefix and 'Store' suffix
export const useMetricsStore = defineStore("metrics", () => {
  // State: camelCase
  const metrics = ref<Metric[]>([]);
  const isLoading = ref(false);
  const errorMessage = ref<string | null>(null);

  // Getters (computed): camelCase
  const metricCount = computed(() => metrics.value.length);
  const hasMetrics = computed(() => metrics.value.length > 0);

  // Actions: camelCase
  const fetchMetrics = async (query: MetricQuery) => {
    // Implementation
  };

  const clearMetrics = () => {
    metrics.value = [];
  };

  return {
    metrics,
    isLoading,
    errorMessage,
    metricCount,
    hasMetrics,
    fetchMetrics,
    clearMetrics,
  };
});
```

### API Clients

```typescript
// api/metrics.ts

// API object: camelCase with 'Api' suffix
export const metricsApi = {
  // Methods: camelCase
  async query(params: MetricQuery): Promise<MetricResponse> {
    // Implementation
  },

  async getTimeSeries(metricId: string): Promise<TimeSeriesResponse> {
    // Implementation
  },
};
```

### Constants

```typescript
// utils/constants.ts

// Constants: SCREAMING_SNAKE_CASE
export const DEFAULT_REFRESH_INTERVAL = 5000;
export const MAX_RETRY_ATTEMPTS = 3;
export const API_TIMEOUT = 30000;

// Constant arrays/objects: SCREAMING_SNAKE_CASE
export const CHART_TYPES = ["line", "bar", "area"] as const;
export const LOG_LEVELS = ["debug", "info", "warn", "error"] as const;

// Configuration objects: camelCase
export const chartConfig = {
  defaultHeight: "400px",
  animationDuration: 300,
};
```

## CSS/SCSS Naming

### Class Names

```scss
// BEM-style naming: kebab-case with double underscores and dashes
.metric-chart {
  // Block

  &__header {
    // Element
  }

  &__title {
    // Element
  }

  &--loading {
    // Modifier
  }

  &--error {
    // Modifier
  }
}

// Utility classes: kebab-case
.text-center {
  text-align: center;
}

.mt-4 {
  margin-top: 1rem;
}
```

### SCSS Variables

```scss
// variables.scss

// Variables: kebab-case with $ prefix
$primary-color: #1890ff;
$secondary-color: #52c41a;
$text-color: #333;
$background-color: #fff;

// Spacing variables
$spacing-xs: 4px;
$spacing-sm: 8px;
$spacing-md: 16px;
$spacing-lg: 24px;

// Font sizes
$font-size-sm: 12px;
$font-size-base: 14px;
$font-size-lg: 16px;
```

## Environment Variables

```bash
# Naming: SCREAMING_SNAKE_CASE with TELEMETRYFLOW_ prefix
TELEMETRYFLOW_APP_TITLE=TelemetryFlow-Viz
TELEMETRYFLOW_API_URL=http://localhost:4318
TELEMETRYFLOW_WS_URL=ws://localhost:4319
TELEMETRYFLOW_USE_MOCK=true
TELEMETRYFLOW_REFRESH_INTERVAL=5000
```

## Route Naming

```typescript
// router/index.ts

const routes = [
  {
    path: "/",
    name: "home", // kebab-case
    component: () => import("@/views/home/index.vue"),
  },
  {
    path: "/metrics",
    name: "metrics", // kebab-case
    component: () => import("@/views/telemetry/metrics/index.vue"),
  },
  {
    path: "/metrics/:id",
    name: "metric-detail", // kebab-case with dash
    component: () => import("@/views/telemetry/metrics/detail.vue"),
  },
];
```

## Directory Structure Naming

```
src/
├── api/              # kebab-case
├── components/       # kebab-case
│   ├── charts/       # kebab-case
│   └── common/       # kebab-case
├── composables/      # kebab-case
├── config/           # kebab-case
├── layouts/          # kebab-case
├── mocks/            # kebab-case
├── router/           # kebab-case
├── services/         # kebab-case
├── store/            # kebab-case
├── streaming/        # kebab-case
├── styles/           # kebab-case
├── types/            # kebab-case
├── utils/            # kebab-case
└── views/            # kebab-case
```

## Import/Export Naming

```typescript
// Named exports: match the exported item's case
export { TimeSeriesChart } from "./TimeSeriesChart.vue";
export { useChartGroup } from "./useChartGroup";
export { metricsApi } from "./metrics";
export type { Metric, MetricQuery } from "./types";

// Default exports: PascalCase for components, camelCase for others
export default TimeSeriesChart; // Component
export default metricsApi; // API client
```

## Event Naming

```typescript
// Custom events: kebab-case
emit('update:value', newValue);
emit('chart-zoom', zoomRange);
emit('data-loaded', data);
emit('error-occurred', error);

// Native events: lowercase
@click="handleClick"
@input="handleInput"
@change="handleChange"
```

## Validation Checklist

Before committing code, verify:

### File Names

- [ ] Vue components use PascalCase (except page components)
- [ ] TypeScript files use kebab-case
- [ ] Composables start with `use` prefix
- [ ] No spaces or special characters in file names

### Code Names

- [ ] Variables and functions use camelCase
- [ ] Interfaces and types use PascalCase
- [ ] Constants use SCREAMING_SNAKE_CASE
- [ ] CSS classes use kebab-case
- [ ] Component props use camelCase in script, kebab-case in template

### Consistency

- [ ] Naming follows established patterns in codebase
- [ ] No mixing of naming conventions
- [ ] Import paths use correct casing

## Quick Reference

| Item                     | Convention           | Example                  |
| ------------------------ | -------------------- | ------------------------ |
| Vue Component (reusable) | PascalCase           | `TimeSeriesChart.vue`    |
| Vue Component (page)     | kebab-case           | `index.vue`              |
| Composable               | camelCase + `use`    | `useChartGroup.ts`       |
| Store                    | kebab-case           | `metrics.ts`             |
| Type/Interface           | PascalCase           | `Metric`, `IMetric`      |
| Variable/Function        | camelCase            | `fetchData`, `isLoading` |
| Constant                 | SCREAMING_SNAKE_CASE | `DEFAULT_TIMEOUT`        |
| CSS Class                | kebab-case           | `metric-chart`           |
| Event                    | kebab-case           | `chart-zoom`             |
| Route Name               | kebab-case           | `metric-detail`          |
| Env Variable             | SCREAMING_SNAKE_CASE | `TELEMETRYFLOW_API_URL`  |

This naming convention ensures consistency and maintainability across the TelemetryFlow-Viz codebase.
