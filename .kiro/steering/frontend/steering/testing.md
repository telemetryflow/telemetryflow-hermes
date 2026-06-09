# Testing Guide for TelemetryFlow-Viz

This document outlines testing strategies and patterns for the Vue.js visualization dashboard.

## Testing Philosophy

- **Test behavior, not implementation**: Focus on what the component does, not how it does it
- **User-centric testing**: Test from the user's perspective
- **Maintainable tests**: Write tests that are easy to understand and update
- **Fast feedback**: Keep tests fast to encourage frequent running

## Testing Stack

### Core Testing Tools

- **Test Runner**: Vitest (fast, Vite-native test runner)
- **Component Testing**: @vue/test-utils (official Vue testing library)
- **Assertions**: Vitest's built-in assertions (Jest-compatible)
- **Mocking**: Vitest's mocking utilities
- **Coverage**: Vitest coverage with c8/istanbul

### Installation

```bash
pnpm add -D vitest @vue/test-utils @vitest/ui happy-dom
```

### Configuration

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";
import vue from "@vitejs/plugin-vue";
import { resolve } from "path";

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: "happy-dom",
    coverage: {
      provider: "c8",
      reporter: ["text", "json", "html"],
      exclude: [
        "node_modules/",
        "src/types/",
        "**/*.d.ts",
        "**/*.config.*",
        "**/mockData",
        "dist/",
      ],
    },
    setupFiles: ["./src/tests/setup.ts"],
  },
  resolve: {
    alias: {
      "@": resolve(__dirname, "./src"),
    },
  },
});
```

## Test Structure

### Directory Organization

```
src/
├── components/
│   ├── charts/
│   │   ├── TimeSeriesChart.vue
│   │   └── __tests__/
│   │       └── TimeSeriesChart.spec.ts
│   └── common/
│       ├── DataTable.vue
│       └── __tests__/
│           └── DataTable.spec.ts
├── composables/
│   ├── useChartGroup.ts
│   └── __tests__/
│       └── useChartGroup.spec.ts
├── store/
│   ├── metrics.ts
│   └── __tests__/
│       └── metrics.spec.ts
├── utils/
│   ├── format.ts
│   └── __tests__/
│       └── format.spec.ts
└── tests/
    ├── setup.ts           # Global test setup
    ├── helpers.ts         # Test helpers
    └── fixtures/          # Test fixtures
        ├── metrics.ts
        ├── logs.ts
        └── traces.ts
```

## Component Testing Patterns

### Basic Component Test

```typescript
// components/charts/__tests__/TimeSeriesChart.spec.ts
import { describe, it, expect, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import TimeSeriesChart from "../TimeSeriesChart.vue";

describe("TimeSeriesChart", () => {
  it("renders chart container", () => {
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

  it("displays loading state", () => {
    const wrapper = mount(TimeSeriesChart, {
      props: {
        data: [],
        loading: true,
      },
    });

    expect(wrapper.find(".loading-spinner").exists()).toBe(true);
  });

  it("emits chart-zoom event when zoomed", async () => {
    const wrapper = mount(TimeSeriesChart, {
      props: {
        data: [{ timestamp: 1000, value: 10 }],
      },
    });

    await wrapper.vm.handleZoom({ start: 0, end: 100 });

    expect(wrapper.emitted("chart-zoom")).toBeTruthy();
    expect(wrapper.emitted("chart-zoom")?.[0]).toEqual([
      { start: 0, end: 100 },
    ]);
  });
});
```

### Testing with Props

```typescript
describe("StatCard", () => {
  it("displays title and value", () => {
    const wrapper = mount(StatCard, {
      props: {
        title: "Total Requests",
        value: 1234,
        unit: "req/s",
      },
    });

    expect(wrapper.text()).toContain("Total Requests");
    expect(wrapper.text()).toContain("1234");
    expect(wrapper.text()).toContain("req/s");
  });

  it("applies custom class when provided", () => {
    const wrapper = mount(StatCard, {
      props: {
        title: "Test",
        value: 100,
        customClass: "custom-stat",
      },
    });

    expect(wrapper.classes()).toContain("custom-stat");
  });
});
```

### Testing with Slots

```typescript
describe("ChartCard", () => {
  it("renders header slot content", () => {
    const wrapper = mount(ChartCard, {
      slots: {
        header: '<div class="custom-header">Custom Header</div>',
      },
    });

    expect(wrapper.find(".custom-header").text()).toBe("Custom Header");
  });

  it("renders default slot content", () => {
    const wrapper = mount(ChartCard, {
      slots: {
        default: '<div class="chart-content">Chart</div>',
      },
    });

    expect(wrapper.find(".chart-content").exists()).toBe(true);
  });
});
```

### Testing User Interactions

```typescript
describe("TraceFilterSidebar", () => {
  it("updates filter when input changes", async () => {
    const wrapper = mount(TraceFilterSidebar);

    const input = wrapper.find('input[type="text"]');
    await input.setValue("api-gateway");

    expect(wrapper.emitted("update:filter")?.[0]).toEqual(["api-gateway"]);
  });

  it("calls onApply when apply button clicked", async () => {
    const onApply = vi.fn();
    const wrapper = mount(TraceFilterSidebar, {
      props: {
        onApply,
      },
    });

    await wrapper.find(".apply-button").trigger("click");

    expect(onApply).toHaveBeenCalledOnce();
  });
});
```

### Testing with Naive UI Components

```typescript
import { NButton, NDataTable } from "naive-ui";

describe("DataTableCard", () => {
  it("renders Naive UI data table", () => {
    const wrapper = mount(DataTableCard, {
      props: {
        data: [{ id: 1, name: "Test" }],
        columns: [
          { key: "id", title: "ID" },
          { key: "name", title: "Name" },
        ],
      },
      global: {
        components: {
          NDataTable,
        },
      },
    });

    expect(wrapper.findComponent(NDataTable).exists()).toBe(true);
  });
});
```

## Composables Testing

```typescript
// composables/__tests__/useChartGroup.spec.ts
import { describe, it, expect } from "vitest";
import { useChartGroup } from "../useChartGroup";

describe("useChartGroup", () => {
  it("initializes with null chart instance", () => {
    const { chartInstance } = useChartGroup({
      groupId: "test-group",
    });

    expect(chartInstance.value).toBeNull();
  });

  it("registers chart instance", () => {
    const { chartInstance, registerChart } = useChartGroup({
      groupId: "test-group",
    });

    const mockChart = { id: "chart-1" };
    registerChart(mockChart);

    expect(chartInstance.value).toBe(mockChart);
  });

  it("syncs zoom across charts", () => {
    const { zoomRange, syncZoom } = useChartGroup({
      groupId: "test-group",
      syncZoom: true,
    });

    const range = { start: 0, end: 100 };
    syncZoom(range);

    expect(zoomRange.value).toEqual(range);
  });
});
```

## Store Testing

```typescript
// store/__tests__/metrics.spec.ts
import { describe, it, expect, beforeEach, vi } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useMetricsStore } from "../metrics";
import { metricsApi } from "@/api/metrics";

vi.mock("@/api/metrics");

describe("useMetricsStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("initializes with empty metrics", () => {
    const store = useMetricsStore();

    expect(store.metrics).toEqual([]);
    expect(store.loading).toBe(false);
    expect(store.error).toBeNull();
  });

  it("fetches metrics successfully", async () => {
    const mockMetrics = [{ id: "1", name: "cpu_usage", value: 50 }];

    vi.mocked(metricsApi.query).mockResolvedValue({
      data: mockMetrics,
    });

    const store = useMetricsStore();
    await store.fetchMetrics({ name: "cpu_usage" });

    expect(store.metrics).toEqual(mockMetrics);
    expect(store.loading).toBe(false);
    expect(store.error).toBeNull();
  });

  it("handles fetch error", async () => {
    vi.mocked(metricsApi.query).mockRejectedValue(new Error("Network error"));

    const store = useMetricsStore();

    await expect(store.fetchMetrics({ name: "cpu_usage" })).rejects.toThrow(
      "Network error",
    );

    expect(store.error).toBe("Network error");
    expect(store.loading).toBe(false);
  });

  it("computes metricCount correctly", () => {
    const store = useMetricsStore();
    store.metrics = [
      { id: "1", name: "metric1", value: 10 },
      { id: "2", name: "metric2", value: 20 },
    ];

    expect(store.metricCount).toBe(2);
  });

  it("clears metrics", () => {
    const store = useMetricsStore();
    store.metrics = [{ id: "1", name: "test", value: 10 }];
    store.error = "Some error";

    store.clearMetrics();

    expect(store.metrics).toEqual([]);
    expect(store.error).toBeNull();
  });
});
```

## Utility Function Testing

```typescript
// utils/__tests__/format.spec.ts
import { describe, it, expect } from "vitest";
import { formatDuration, formatBytes, formatNumber } from "../format";

describe("format utilities", () => {
  describe("formatDuration", () => {
    it("formats milliseconds", () => {
      expect(formatDuration(500)).toBe("500ms");
    });

    it("formats seconds", () => {
      expect(formatDuration(5000)).toBe("5.00s");
    });

    it("formats minutes", () => {
      expect(formatDuration(120000)).toBe("2.00m");
    });
  });

  describe("formatBytes", () => {
    it("formats bytes", () => {
      expect(formatBytes(500)).toBe("500 B");
    });

    it("formats kilobytes", () => {
      expect(formatBytes(1024)).toBe("1.00 KB");
    });

    it("formats megabytes", () => {
      expect(formatBytes(1048576)).toBe("1.00 MB");
    });
  });

  describe("formatNumber", () => {
    it("formats with commas", () => {
      expect(formatNumber(1234567)).toBe("1,234,567");
    });

    it("formats with decimals", () => {
      expect(formatNumber(1234.56, 2)).toBe("1,234.56");
    });
  });
});
```

## API Client Testing

```typescript
// api/__tests__/metrics.spec.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import axios from "axios";
import { metricsApi } from "../metrics";

vi.mock("axios");

describe("metricsApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("queries metrics", async () => {
    const mockResponse = {
      data: {
        data: [{ id: "1", name: "cpu_usage", value: 50 }],
      },
    };

    vi.mocked(axios.post).mockResolvedValue(mockResponse);

    const result = await metricsApi.query({
      name: "cpu_usage",
      timeRange: { start: 0, end: 1000 },
    });

    expect(result.data).toEqual(mockResponse.data.data);
    expect(axios.post).toHaveBeenCalledWith(
      "/v2/metrics/query",
      expect.objectContaining({ name: "cpu_usage" }),
    );
  });

  it("handles API errors", async () => {
    vi.mocked(axios.post).mockRejectedValue(new Error("API Error"));

    await expect(metricsApi.query({ name: "cpu_usage" })).rejects.toThrow(
      "API Error",
    );
  });
});
```

## Test Fixtures

```typescript
// tests/fixtures/metrics.ts
import type { Metric } from "@/types/metric";

export const createMockMetric = (overrides?: Partial<Metric>): Metric => ({
  id: "metric-1",
  name: "http_requests_total",
  value: 100,
  timestamp: Date.now(),
  labels: {
    service: "api-gateway",
    method: "GET",
  },
  ...overrides,
});

export const createMockMetrics = (count: number): Metric[] => {
  return Array.from({ length: count }, (_, i) =>
    createMockMetric({
      id: `metric-${i + 1}`,
      value: Math.random() * 100,
    }),
  );
};
```

## Test Helpers

```typescript
// tests/helpers.ts
import { mount } from "@vue/test-utils";
import { createPinia } from "pinia";
import { createRouter, createMemoryHistory } from "vue-router";

export function mountWithProviders(component: any, options = {}) {
  const pinia = createPinia();
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [],
  });

  return mount(component, {
    global: {
      plugins: [pinia, router],
      ...options.global,
    },
    ...options,
  });
}

export function flushPromises() {
  return new Promise((resolve) => setTimeout(resolve, 0));
}
```

## Coverage Requirements

### Target Coverage

- **Statements**: ≥80%
- **Branches**: ≥75%
- **Functions**: ≥80%
- **Lines**: ≥80%

### Coverage Configuration

```json
// package.json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:watch": "vitest --watch"
  }
}
```

## Best Practices

### DO ✅

1. **Test user behavior**: Focus on what users see and do
2. **Use data-testid**: For elements that need to be tested
3. **Mock external dependencies**: API calls, third-party libraries
4. **Test edge cases**: Empty states, errors, loading states
5. **Keep tests isolated**: Each test should be independent
6. **Use descriptive test names**: Clearly state what is being tested
7. **Test accessibility**: Ensure components are accessible

### DON'T ❌

1. **Test implementation details**: Avoid testing internal state
2. **Test third-party libraries**: Trust that they work
3. **Write brittle tests**: Tests that break with minor changes
4. **Ignore async operations**: Always await async operations
5. **Test everything**: Focus on critical paths and edge cases
6. **Duplicate tests**: One test per behavior

## Running Tests

```bash
# Run all tests
pnpm test

# Run tests in watch mode
pnpm test:watch

# Run tests with coverage
pnpm test:coverage

# Run tests with UI
pnpm test:ui

# Run specific test file
pnpm test src/components/charts/__tests__/TimeSeriesChart.spec.ts

# Run tests matching pattern
pnpm test --grep "TimeSeriesChart"
```

## Continuous Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
        with:
          version: 9
      - uses: actions/setup-node@v3
        with:
          node-version: 20
          cache: "pnpm"
      - run: pnpm install
      - run: pnpm test:coverage
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
```

This testing guide ensures comprehensive, maintainable tests for TelemetryFlow-Viz.
