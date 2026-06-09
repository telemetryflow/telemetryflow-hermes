# Vue 3 Development Patterns

This document outlines the Vue 3 development patterns and best practices for TelemetryFlow-Viz.

## Vue 3 Composition API Patterns

### Script Setup Syntax

Use `<script setup>` for all new components:

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import type { Metric } from "@/types/metric";

// Props
interface Props {
  metricId: string;
  showLegend?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  showLegend: true,
});

// Emits
const emit = defineEmits<{
  "update:value": [value: number];
  "chart-zoom": [range: { start: number; end: number }];
}>();

// Reactive state
const loading = ref(false);
const data = ref<Metric[]>([]);

// Computed properties
const filteredData = computed(() => {
  return data.value.filter((m) => m.value > 0);
});

// Methods
const fetchData = async () => {
  loading.value = true;
  try {
    // Fetch data
  } finally {
    loading.value = false;
  }
};

// Lifecycle hooks
onMounted(() => {
  fetchData();
});
</script>

<template>
  <div class="metric-chart">
    <LoadingSpinner v-if="loading" />
    <div v-else>
      <!-- Chart content -->
    </div>
  </div>
</template>

<style scoped lang="scss">
.metric-chart {
  // Styles
}
</style>
```

### Composables Pattern

Create reusable composition functions:

```typescript
// composables/useChartGroup.ts
import { ref, onUnmounted } from "vue";

export interface ChartGroupOptions {
  groupId: string;
  syncZoom?: boolean;
}

export function useChartGroup(options: ChartGroupOptions) {
  const chartInstance = ref<any>(null);
  const zoomRange = ref<{ start: number; end: number } | null>(null);

  const registerChart = (instance: any) => {
    chartInstance.value = instance;
    // Register with group manager
  };

  const syncZoom = (range: { start: number; end: number }) => {
    zoomRange.value = range;
    // Sync with other charts in group
  };

  onUnmounted(() => {
    // Cleanup
  });

  return {
    chartInstance,
    zoomRange,
    registerChart,
    syncZoom,
  };
}
```

Usage:

```vue
<script setup lang="ts">
import { useChartGroup } from "@/composables/useChartGroup";

const { chartInstance, syncZoom } = useChartGroup({
  groupId: "metrics-overview",
  syncZoom: true,
});
</script>
```

## Pinia Store Patterns

### Store Definition

```typescript
// store/metrics.ts
import { defineStore } from "pinia";
import type { Metric, MetricQuery } from "@/types/metric";
import { metricsApi } from "@/api/metrics";

export const useMetricsStore = defineStore("metrics", () => {
  // State
  const metrics = ref<Metric[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const currentQuery = ref<MetricQuery | null>(null);

  // Getters (computed)
  const metricCount = computed(() => metrics.value.length);
  const hasMetrics = computed(() => metrics.value.length > 0);
  const metricsByService = computed(() => {
    return metrics.value.reduce(
      (acc, metric) => {
        const service = metric.labels.service || "unknown";
        if (!acc[service]) acc[service] = [];
        acc[service].push(metric);
        return acc;
      },
      {} as Record<string, Metric[]>,
    );
  });

  // Actions
  const fetchMetrics = async (query: MetricQuery) => {
    loading.value = true;
    error.value = null;
    currentQuery.value = query;

    try {
      const response = await metricsApi.query(query);
      metrics.value = response.data;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Failed to fetch metrics";
      throw e;
    } finally {
      loading.value = false;
    }
  };

  const clearMetrics = () => {
    metrics.value = [];
    currentQuery.value = null;
    error.value = null;
  };

  const updateMetric = (id: string, updates: Partial<Metric>) => {
    const index = metrics.value.findIndex((m) => m.id === id);
    if (index !== -1) {
      metrics.value[index] = { ...metrics.value[index], ...updates };
    }
  };

  return {
    // State
    metrics,
    loading,
    error,
    currentQuery,
    // Getters
    metricCount,
    hasMetrics,
    metricsByService,
    // Actions
    fetchMetrics,
    clearMetrics,
    updateMetric,
  };
});
```

### Store Usage in Components

```vue
<script setup lang="ts">
import { useMetricsStore } from "@/store/metrics";
import { storeToRefs } from "pinia";

const metricsStore = useMetricsStore();

// Use storeToRefs for reactive state
const { metrics, loading, metricCount } = storeToRefs(metricsStore);

// Actions can be called directly
const loadMetrics = () => {
  metricsStore.fetchMetrics({
    name: "http_requests_total",
    timeRange: { start: Date.now() - 3600000, end: Date.now() },
  });
};
</script>
```

## Component Patterns

### Chart Component Pattern

```vue
<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { use } from "echarts/core";
import { LineChart } from "echarts/charts";
import { GridComponent, TooltipComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import VChart from "vue-echarts";
import type { EChartsOption } from "echarts";

// Register ECharts components
use([LineChart, GridComponent, TooltipComponent, CanvasRenderer]);

interface Props {
  data: Array<{ timestamp: number; value: number }>;
  title?: string;
  height?: string;
  showDataPoints?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  height: "400px",
  showDataPoints: true,
});

const emit = defineEmits<{
  "chart-zoom": [range: { start: number; end: number }];
}>();

const chartRef = ref<InstanceType<typeof VChart>>();

const chartOptions = computed<EChartsOption>(() => ({
  title: {
    text: props.title,
    left: "center",
  },
  tooltip: {
    trigger: "axis",
  },
  xAxis: {
    type: "time",
  },
  yAxis: {
    type: "value",
  },
  series: [
    {
      type: "line",
      data: props.data.map((d) => [d.timestamp, d.value]),
      smooth: true,
      showSymbol: props.showDataPoints,
    },
  ],
  dataZoom: [
    {
      type: "inside",
    },
  ],
}));

const handleZoom = (params: any) => {
  emit("chart-zoom", {
    start: params.start,
    end: params.end,
  });
};

onMounted(() => {
  if (chartRef.value) {
    chartRef.value.chart?.on("datazoom", handleZoom);
  }
});
</script>

<template>
  <div class="chart-container">
    <VChart
      ref="chartRef"
      :option="chartOptions"
      :style="{ height }"
      autoresize
    />
  </div>
</template>

<style scoped lang="scss">
.chart-container {
  width: 100%;
  position: relative;
}
</style>
```

### Data Table Component Pattern

```vue
<script setup lang="ts">
import { ref, computed } from "vue";
import type { DataTableColumns } from "naive-ui";

interface Props {
  data: any[];
  columns: DataTableColumns;
  loading?: boolean;
  pagination?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  pagination: true,
});

const emit = defineEmits<{
  "row-click": [row: any];
  "update:page": [page: number];
}>();

const currentPage = ref(1);
const pageSize = ref(20);

const paginatedData = computed(() => {
  if (!props.pagination) return props.data;
  const start = (currentPage.value - 1) * pageSize.value;
  return props.data.slice(start, start + pageSize.value);
});

const handleRowClick = (row: any) => {
  emit("row-click", row);
};

const handlePageChange = (page: number) => {
  currentPage.value = page;
  emit("update:page", page);
};
</script>

<template>
  <n-data-table
    :columns="columns"
    :data="paginatedData"
    :loading="loading"
    :pagination="
      pagination
        ? {
            page: currentPage,
            pageSize: pageSize,
            itemCount: data.length,
            onChange: handlePageChange,
          }
        : false
    "
    @row-click="handleRowClick"
  />
</template>
```

## TypeScript Patterns

### Type Definitions

```typescript
// types/metric.ts
export interface Metric {
  id: string;
  name: string;
  value: number;
  timestamp: number;
  labels: Record<string, string>;
  metadata?: MetricMetadata;
}

export interface MetricMetadata {
  unit: string;
  description?: string;
  type: "counter" | "gauge" | "histogram" | "summary";
}

export interface MetricQuery {
  name: string;
  labels?: Record<string, string>;
  timeRange: {
    start: number;
    end: number;
  };
  step?: number;
}

export type MetricTimeSeries = Array<{
  timestamp: number;
  value: number;
}>;
```

### API Client Pattern

```typescript
// api/metrics.ts
import axios from "axios";
import type { Metric, MetricQuery, MetricTimeSeries } from "@/types/metric";

const api = axios.create({
  baseURL: import.meta.env.TELEMETRYFLOW_API_URL,
  timeout: 30000,
});

export const metricsApi = {
  async query(query: MetricQuery): Promise<{ data: Metric[] }> {
    const response = await api.post("/v2/metrics/query", query);
    return response.data;
  },

  async getTimeSeries(metricId: string): Promise<{ data: MetricTimeSeries }> {
    const response = await api.get(`/v2/metrics/${metricId}/timeseries`);
    return response.data;
  },

  async getMetadata(metricName: string): Promise<{ data: MetricMetadata }> {
    const response = await api.get(`/v2/metrics/${metricName}/metadata`);
    return response.data;
  },
};
```

## Router Patterns

### Route Definition

```typescript
// router/index.ts
import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "home",
    component: () => import("@/views/home/index.vue"),
    meta: { title: "Home", requiresAuth: true },
  },
  {
    path: "/metrics",
    name: "metrics",
    component: () => import("@/views/telemetry/metrics/index.vue"),
    meta: { title: "Metrics", requiresAuth: true },
  },
  {
    path: "/metrics/:id",
    name: "metric-detail",
    component: () => import("@/views/telemetry/metrics/detail.vue"),
    meta: { title: "Metric Detail", requiresAuth: true },
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.TELEMETRYFLOW_BASE_URL),
  routes,
});

// Navigation guards
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    next({ name: "login" });
  } else {
    next();
  }
});

export default router;
```

## Mock Data Patterns

### Mock Data Generator

```typescript
// mocks/metrics.ts
import { SERVICES, OPERATIONS, randomInt, randomFloat } from "./shared";
import type { Metric, MetricTimeSeries } from "@/types/metric";

export function generateMetricNames(): string[] {
  return [
    "http_requests_total",
    "http_request_duration_seconds",
    "http_response_size_bytes",
    "cpu_usage_percent",
    "memory_usage_bytes",
    "disk_io_operations_total",
  ];
}

export function generateMetricTimeSeries(
  metricName: string,
  duration: number = 3600000,
): MetricTimeSeries {
  const now = Date.now();
  const points: MetricTimeSeries = [];
  const step = 60000; // 1 minute

  for (let t = now - duration; t <= now; t += step) {
    points.push({
      timestamp: t,
      value: randomFloat(0, 100),
    });
  }

  return points;
}

export const metricsMock = {
  generateMetricNames,
  generateMetricTimeSeries,
  // ... other mock functions
};
```

## Error Handling Patterns

### Global Error Handler

```typescript
// main.ts
import { createApp } from "vue";
import App from "./App.vue";

const app = createApp(App);

app.config.errorHandler = (err, instance, info) => {
  console.error("Global error:", err);
  console.error("Component:", instance);
  console.error("Error info:", info);

  // Send to error tracking service
  // trackError(err, { component: instance, info });
};

app.mount("#app");
```

### Component Error Handling

```vue
<script setup lang="ts">
import { ref, onErrorCaptured } from "vue";

const error = ref<Error | null>(null);

onErrorCaptured((err) => {
  error.value = err;
  console.error("Component error:", err);
  return false; // Prevent propagation
});
</script>

<template>
  <div v-if="error" class="error-state">
    <p>An error occurred: {{ error.message }}</p>
  </div>
  <div v-else>
    <!-- Normal content -->
  </div>
</template>
```

## Performance Patterns

### Lazy Loading

```typescript
// router/index.ts
const routes = [
  {
    path: "/traces",
    component: () => import("@/views/telemetry/traces/index.vue"),
  },
];
```

### Virtual Scrolling for Large Lists

```vue
<script setup lang="ts">
import { ref } from "vue";

const logs = ref<Log[]>([]); // Large array

// Use Naive UI's virtual list
</script>

<template>
  <n-virtual-list :items="logs" :item-size="50" style="height: 600px">
    <template #default="{ item }">
      <LogItem :log="item" />
    </template>
  </n-virtual-list>
</template>
```

### Debouncing and Throttling

```typescript
import { ref, watch } from "vue";
import { useDebounceFn, useThrottleFn } from "@vueuse/core";

const searchQuery = ref("");

const debouncedSearch = useDebounceFn((query: string) => {
  // Perform search
}, 300);

watch(searchQuery, (newQuery) => {
  debouncedSearch(newQuery);
});
```

## Testing Patterns

### Component Testing

```typescript
// components/__tests__/TimeSeriesChart.spec.ts
import { mount } from "@vue/test-utils";
import { describe, it, expect } from "vitest";
import TimeSeriesChart from "../TimeSeriesChart.vue";

describe("TimeSeriesChart", () => {
  it("renders chart with data", () => {
    const wrapper = mount(TimeSeriesChart, {
      props: {
        data: [
          { timestamp: 1000, value: 10 },
          { timestamp: 2000, value: 20 },
        ],
      },
    });

    expect(wrapper.find(".chart-container").exists()).toBe(true);
  });

  it("emits chart-zoom event", async () => {
    const wrapper = mount(TimeSeriesChart, {
      props: {
        data: [],
      },
    });

    // Simulate zoom
    await wrapper.vm.handleZoom({ start: 0, end: 100 });

    expect(wrapper.emitted("chart-zoom")).toBeTruthy();
  });
});
```

## Best Practices

1. **Use Composition API**: Prefer `<script setup>` over Options API
2. **Type Everything**: Use TypeScript for all components and functions
3. **Composables for Reusability**: Extract common logic into composables
4. **Pinia for State**: Use Pinia stores for global state management
5. **Lazy Loading**: Use dynamic imports for routes and large components
6. **Error Boundaries**: Implement error handling at component level
7. **Performance**: Use virtual scrolling, debouncing, and memoization
8. **Testing**: Write unit tests for critical components and composables
9. **Accessibility**: Use semantic HTML and ARIA attributes
10. **Code Splitting**: Leverage Vite's automatic code splitting

This guide ensures consistent, maintainable, and performant Vue 3 code across TelemetryFlow-Viz.
