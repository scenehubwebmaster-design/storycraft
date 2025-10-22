# StoryCraft Performance Optimization Guide

## 🚀 Development Server Performance

### Quick Start Commands

```powershell
# Standard development (balanced performance)
npm run dev:all

# Fast development mode (reduced logging)
npm run dev:all:fast

# Production mode (multi-worker, maximum performance)
npm start:prod
```

## Backend Optimizations (FastAPI + Uvicorn)

### Current Configuration

The `uvicorn_config.py` provides optimized settings:

**Development Mode:**

- Single worker with hot reload
- Fast file watching (excludes .pyc, .db, **pycache**)
- Info-level logging for debugging
- Automatic loop selection (uvloop if available)
- Automatic HTTP implementation (httptools if available)

**Production Mode:**

- Multiple workers: `(CPU cores × 2) + 1`, capped at 16
- No reload overhead
- Warning-level logging only
- Access logs disabled for performance
- Connection backlog: 2048
- Concurrent connections: 1000
- Keep-alive timeout: 65s

### Performance Settings Explained

1. **Loop**: `uvloop` is 2-4x faster than standard asyncio

   - Automatically used if installed (already in requirements.txt via uvicorn[standard])

2. **HTTP**: `httptools` is faster than h11

   - Automatically used if installed (already in requirements.txt via uvicorn[standard])

3. **Workers**:

   - Development: 1 (for hot reload)
   - Production: CPU cores × 2 + 1 (optimal for I/O bound workloads)
   - Max: 16 (prevents over-allocation)

4. **Backlog**: 2048 connections queued before rejecting
5. **Concurrency Limit**: 1000 simultaneous connections

### Environment Variables

```powershell
# Development mode (default)
$env:DEV_MODE="true"

# Production mode
$env:DEV_MODE="false"
```

## Frontend Optimizations (Vite + React)

### Vite Configuration Improvements

1. **Fast Refresh**: Enabled with React Fast Refresh optimizations
2. **File Watching**: Native file watching (not polling) for faster change detection
3. **Ignored Paths**: node_modules, dist, .git excluded from watching
4. **HMR**: Hot Module Replacement with overlay for errors
5. **WebSocket**: Enabled for proxy to support real-time features

### Build Optimizations

1. **Code Splitting**:

   - Vendor bundle: React core libraries
   - MUI bundle: Material-UI components
   - Better caching and parallel downloads

2. **Dependency Pre-bundling**:
   - Common dependencies pre-bundled for faster dev server start
   - Includes: React, React Router, MUI, axios

### Chunk Size Limit

Increased to 1000KB to reduce warnings for large bundles. Consider:

- Dynamic imports for large features
- Route-based code splitting
- Lazy loading for heavy components

## System Requirements for Best Performance

### Recommended:

- **CPU**: 8+ cores (enables 17 workers in production)
- **RAM**: 16GB+ (for concurrent builds and multiple workers)
- **SSD**: NVMe SSD for fast file I/O
- **Node**: v18+ (better performance, native fetch)
- **Python**: 3.11+ (faster than 3.10, nearly as fast as 3.12)

### Minimal:

- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: SSD (HDD will be significantly slower)
- **Node**: v16+
- **Python**: 3.9+

## Performance Monitoring

### Backend Health Check

```powershell
curl http://localhost:8000/health
```

Response time should be < 50ms for healthy server.

### Frontend Dev Server

Vite dev server typically starts in < 1 second.
Hot reload should be near-instantaneous (< 100ms).

### Production Benchmarking

```powershell
# Install Apache Bench (optional)
# Windows: Download from Apache website

# Test API performance
ab -n 1000 -c 10 http://localhost:8000/health
```

Expected results with production config:

- Requests/second: 1000+ (simple endpoints)
- Response time: < 10ms (p50), < 50ms (p99)

## Troubleshooting Performance Issues

### Slow Backend Startup

**Symptom**: Server takes > 5 seconds to start
**Causes**:

- Large database initialization
- Many migrations
- Import overhead

**Solutions**:

```python
# In main.py, conditionally create tables
if os.getenv("INIT_DB", "false").lower() == "true":
    Base.metadata.create_all(bind=engine)
```

### Slow Hot Reload

**Symptom**: Changes take > 2 seconds to reflect
**Causes**:

- File watching too many files
- Antivirus scanning
- HDD storage

**Solutions**:

1. Add more exclusions to vite.config.js watch.ignored
2. Exclude project directory from antivirus real-time scanning
3. Move project to SSD

### High Memory Usage

**Symptom**: > 4GB RAM usage during development

**Backend**:

```python
# Reduce workers in uvicorn_config.py
workers = min(cpu_count, 4)  # Cap at 4 instead of 16
```

**Frontend**:

```javascript
// In vite.config.js, disable pre-bundling
optimizeDeps: {
  disabled: true; // Trades startup time for memory
}
```

### Port Conflicts

**Symptom**: "Port already in use"

**Solutions**:

```powershell
# Find process using port 3000 (frontend)
netstat -ano | findstr :3000

# Find process using port 8000 (backend)
netstat -ano | findstr :8000

# Kill process by PID
taskkill /PID <PID> /F
```

Or change ports in:

- Frontend: `frontend/vite.config.js` → `server.port`
- Backend: `backend/uvicorn_config.py` → `config["port"]`

## Advanced Optimizations

### Database Connection Pooling

Already configured in `database.py`:

```python
# Optimize pool settings for your workload
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Or QueuePool for production
    pool_size=20,          # Connections per worker
    max_overflow=10,       # Extra connections when needed
)
```

### Caching Strategies

Consider adding Redis for:

- LLM response caching
- Session management
- Rate limiting

### Load Balancing

For production at scale:

1. Run multiple backend instances on different ports
2. Use nginx or Caddy as reverse proxy
3. Implement round-robin or least-connections balancing

### CDN for Frontend

For production deployment:

1. Build frontend: `npm run build`
2. Upload `frontend/dist/` to CDN (Cloudflare, AWS CloudFront)
3. Serve static assets from CDN
4. Backend serves only API endpoints

## Performance Metrics Dashboard

Consider integrating:

- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **OpenTelemetry**: Distributed tracing

Example metrics to track:

- API response times (p50, p95, p99)
- Error rates
- Database query times
- LLM generation times
- Memory/CPU usage per worker

## Conclusion

With these optimizations, you should see:

- **Frontend**: < 1s startup, < 100ms hot reload
- **Backend**: < 2s startup (dev), instant in production
- **API**: < 50ms response time for simple endpoints
- **Concurrency**: Handle 1000+ concurrent requests

For maximum performance in production:

```powershell
# Build frontend
npm run build

# Start optimized production server
npm run start:prod
```

This configuration can handle significant load while maintaining excellent developer experience in development mode.
