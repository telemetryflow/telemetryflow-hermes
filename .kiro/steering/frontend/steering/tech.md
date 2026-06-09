# Technology Stack & Build System

## Core Technologies

- **Framework**: Vue 3.5+ with Composition API and `<script setup>` syntax
- **Language**: TypeScript 5.7 with strict configuration
- **Package Manager**: pnpm 9.15+ (preferred over npm/yarn)
- **Runtime**: Node.js 20+ (Alpine Linux in Docker)
- **Build Tool**: Vite 6.4+ with fast HMR and optimized production builds

## Frontend Stack

- **UI Framework**: Vue 3 with TypeScript
- **Component Library**: Naive UI 2.43+ (comprehensive Vue 3 component library)
- **State Management**: Pinia 3.0+ (official Vue state management)
- **Router**: Vue Router 4.6+ (official Vue routing)
- **Styling**: UnoCSS 0.65+ (atomic CSS engine) + SCSS for custom styles
- **Icons**: Iconify Vue 4.3+ with UnoCSS preset-icons
- **Utilities**: VueUse 12.8+ (collection of Vue composition utilities)

## Data Visualization

- **Charts**: ECharts 5.6+ (powerful charting library)
- **Vue Integration**: vue-echarts 7.0+ (Vue 3 wrapper for ECharts)
- **Chart Types**: Line, Area, Bar, Scatter, Heatmap, Gauge, Flame Graph, Node Graph
- **Features**: Interactive tooltips, zoom, data points, synchronized charts

## HTTP & Real-time Communication

- **HTTP Client**: Axios 1.13+ for REST API calls
- **WebSocket**: Socket.IO Client 4.8+ for real-time streaming
- **API Integration**: TFO-Collector HTTP/gRPC/WebSocket endpoints

## Development Tools

- **Auto Import**: unplugin-auto-import 0.18+ (auto-import Vue APIs, composables, stores)
- **Component Auto-registration**: unplugin-vue-components 0.27+ (auto-register components)
- **Type Checking**: vue-tsc 2.2+ (TypeScript type checker for Vue)
- **Linting**: ESLint 9.39+ with TypeScript and Vue plugins
- **Date/Time**: dayjs 1.11+ (lightweight date library)
- **Utilities**: lodash-es 4.17+ (modular utility library)
- **UUID**: uuid 11.1+ (unique identifier generation)

## Build Configuration

- **Target**: ESNext with modern browser support
- **Minification**: esbuild for fast builds
- **Code Splitting**: Manual chunks for vendors (vue, ui, charts)
- **Source Maps**: Enabled in development mode
- **CSS**: SCSS with modern-compiler API
- **Optimization**: Tree-shaking, chunk splitting, lazy loading

## Common Commands

### Development

```bash
# Start development server with HMR
pnpm dev

# Type checking
pnpm type-check

# Linting with auto-fix
pnpm lint

# Clean build artifacts and dependencies
pnpm clean
```

### Build & Preview

```bash
# Build for production
pnpm build

# Build for development (with source maps)
pnpm build:dev

# Preview production build
pnpm preview
```

### Docker Operations

```bash
# Build Docker image
docker build -t telemetryflow/telemetryflow-viz .

# Run with Docker Compose (local)
docker compose -f docker-compose.local.yml up -d

# Run with Docker Compose (demo with SSL)
docker compose -f docker-compose.demo.yml up -d

# Stop services
docker compose down
```

### SSL Setup (Demo Deployment)

```bash
# Initialize SSL with Let's Encrypt
./config/init-ssl.sh your-domain.com your-email@example.com

# Or manually generate certificate
docker compose -f docker-compose.demo.yml run --rm certbot certonly \
  --webroot --webroot-path=/var/www/certbot \
  --email your-email@example.com \
  --agree-tos --no-eff-email \
  -d your-domain.com

# Restart nginx with SSL
docker compose -f docker-compose.demo.yml restart nginx
```

## Environment Configuration

### Development Environment Variables

| Variable                         | Default                       | Description                 |
| -------------------------------- | ----------------------------- | --------------------------- |
| `TELEMETRYFLOW_APP_TITLE`        | `TelemetryFlow-Viz`           | Application title           |
| `TELEMETRYFLOW_APP_CODE`         | `TFO-Viz`                     | Application code            |
| `TELEMETRYFLOW_BASE_URL`         | `/`                           | Base URL for routing        |
| `TELEMETRYFLOW_API_URL`          | `http://localhost:4318`       | TFO-Collector HTTP endpoint |
| `TELEMETRYFLOW_GRPC_URL`         | `http://localhost:4317`       | TFO-Collector gRPC endpoint |
| `TELEMETRYFLOW_WS_URL`           | `ws://localhost:4319`         | WebSocket endpoint          |
| `TELEMETRYFLOW_USE_MOCK`         | `true` (dev) / `false` (prod) | Enable mock data            |
| `TELEMETRYFLOW_REFRESH_INTERVAL` | `5000`                        | Data refresh interval (ms)  |

### Authentication Environment Variables

| Variable                      | Default        | Description            |
| ----------------------------- | -------------- | ---------------------- |
| `TELEMETRYFLOW_VIZ_ADMIN`     | `admin`        | Admin username         |
| `TELEMETRYFLOW_VIZ_PASSWORD`  | `Admin@654123` | Admin password         |
| `TELEMETRYFLOW_SSO_GOOGLE`    | `false`        | Enable Google SSO      |
| `TELEMETRYFLOW_SSO_MICROSOFT` | `false`        | Enable Microsoft SSO   |
| `TELEMETRYFLOW_SSO_APPLE`     | `false`        | Enable Apple SSO       |
| `TELEMETRYFLOW_SSO_SLACK`     | `false`        | Enable Slack SSO       |
| `TELEMETRYFLOW_SSO_COGNITO`   | `false`        | Enable AWS Cognito SSO |

### Configuration Files

- **Development**: `.env.development` (loaded in dev mode)
- **Production**: `.env.production` (loaded in prod mode)
- **Examples**: `.env.development.example`, `.env.production.example`
- **Docker**: Environment variables in `docker-compose.yml`

## Vite Configuration

### Key Features

- **Path Aliases**: `@` → `src/`, `~` → project root
- **Auto Import**: Vue APIs, composables, stores automatically imported
- **Component Registration**: Components auto-registered from `src/components`
- **Mock Server**: Built-in mock API server for `/v2/*` endpoints
- **Proxy**: API and WebSocket proxying to TFO-Collector
- **CSS Preprocessing**: SCSS with global variables
- **Optimization**: Dependency pre-bundling, code splitting

### Build Output

```
dist/
├── assets/
│   ├── index-[hash].js      # Main application bundle
│   ├── vue-vendor-[hash].js # Vue core dependencies
│   ├── ui-vendor-[hash].js  # Naive UI components
│   ├── chart-vendor-[hash].js # ECharts library
│   └── index-[hash].css     # Compiled styles
├── index.html               # Entry HTML
└── favicon.*                # Favicon files
```

## Performance Considerations

- **Code Splitting**: Vendor chunks separated for better caching
- **Lazy Loading**: Route-based code splitting with dynamic imports
- **Tree Shaking**: Unused code eliminated in production builds
- **Asset Optimization**: Images, fonts, and static assets optimized
- **Dependency Pre-bundling**: Vite pre-bundles dependencies for faster dev server
- **CSS Optimization**: UnoCSS generates minimal atomic CSS

## Browser Support

- **Modern Browsers**: Chrome, Firefox, Safari, Edge (latest 2 versions)
- **Target**: ESNext with native ES modules
- **Polyfills**: Not included (assumes modern browser environment)

## Development Server

- **Host**: `0.0.0.0` (accessible from network)
- **Port**: `3100` (development), `3101` (preview)
- **HMR**: Fast Hot Module Replacement
- **CORS**: Enabled for API development
- **Proxy**: Automatic proxying to backend services
