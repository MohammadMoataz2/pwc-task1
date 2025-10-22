# Load Testing for PWC Contract Analysis API

This directory contains load testing scripts using Locust to validate the performance and scalability of the PWC Contract Analysis API.

## Overview

The load tests simulate realistic user behavior patterns and stress test various components of the system:

- **Authentication flows** (register/login)
- **Contract uploads** and management
- **GenAI analysis** requests
- **Database operations** (CRUD operations)
- **System monitoring** (health checks, metrics, logs)

## Test Files

### 1. `locustfile.py` - Main Load Test
Comprehensive load test simulating normal user behavior:

- **ContractAnalysisUser**: Regular users performing typical operations
- **AdminUser**: Administrative users monitoring the system

**Key Test Scenarios:**
- User registration and authentication
- Contract uploads with client association
- Direct contract analysis via GenAI
- Document analysis by ID
- System metrics and logs access
- Health and readiness checks

### 2. `stress_test.py` - Stress Testing
Focused stress tests for specific system components:

- **HighVolumeUploadUser**: High-frequency contract uploads
- **ConcurrentAnalysisUser**: Concurrent GenAI analysis requests
- **DatabaseStressUser**: Database operation stress testing

## Prerequisites

1. **Install Locust:**
   ```bash
   pip install -r load_tests/requirements.txt
   ```

2. **Ensure API is running:**
   ```bash
   docker-compose up -d
   ```

3. **Verify API accessibility:**
   ```bash
   curl http://localhost:8000/healthz
   ```

## Running Load Tests

### Basic Load Test
```bash
# Run main load test
locust -f load_tests/locustfile.py --host=http://localhost:8000

# Access Web UI at: http://localhost:8089
```

### Stress Test
```bash
# Run stress test scenarios
locust -f load_tests/stress_test.py --host=http://localhost:8000
```

### Command Line Execution (No Web UI)
```bash
# Run with specific parameters
locust -f load_tests/locustfile.py \
  --host=http://localhost:8000 \
  --users=50 \
  --spawn-rate=5 \
  --run-time=300s \
  --headless

# Generate HTML report
locust -f load_tests/locustfile.py \
  --host=http://localhost:8000 \
  --users=100 \
  --spawn-rate=10 \
  --run-time=600s \
  --headless \
  --html=load_test_report.html
```

## Test Configuration

### Recommended Test Scenarios

#### 1. **Normal Load Test**
- **Users**: 10-50 concurrent users
- **Spawn Rate**: 2-5 users per second
- **Duration**: 10-30 minutes
- **Purpose**: Validate normal operation performance

```bash
locust -f load_tests/locustfile.py \
  --host=http://localhost:8000 \
  --users=25 \
  --spawn-rate=3 \
  --run-time=1800s \
  --headless
```

#### 2. **Peak Load Test**
- **Users**: 50-200 concurrent users
- **Spawn Rate**: 5-10 users per second
- **Duration**: 15-45 minutes
- **Purpose**: Test system under peak expected load

```bash
locust -f load_tests/locustfile.py \
  --host=http://localhost:8000 \
  --users=100 \
  --spawn-rate=8 \
  --run-time=2700s \
  --headless
```

#### 3. **Stress Test**
- **Users**: 200+ concurrent users
- **Spawn Rate**: 10+ users per second
- **Duration**: 30+ minutes
- **Purpose**: Find system breaking points

```bash
locust -f load_tests/stress_test.py \
  --host=http://localhost:8000 \
  --users=300 \
  --spawn-rate=15 \
  --run-time=3600s \
  --headless
```

## Metrics to Monitor

### Performance Metrics
- **Response Times**: 95th percentile should be < 2000ms for most endpoints
- **Throughput**: Requests per second (RPS)
- **Error Rate**: Should be < 1% under normal load
- **Concurrent Users**: Maximum supportable users

### System Metrics
- **CPU Usage**: Should stay below 80%
- **Memory Usage**: Monitor for memory leaks
- **Database Connections**: Monitor connection pool usage
- **Disk I/O**: For file storage operations

### API-Specific Metrics
- **Authentication**: Login success rate
- **Contract Upload**: File processing time
- **GenAI Analysis**: AI service response times
- **Database Operations**: Query performance

## Expected Performance Baselines

### Response Time Targets
| Endpoint | Expected Response Time |
|----------|----------------------|
| `/healthz` | < 100ms |
| `/readyz` | < 500ms |
| `POST /auth/login` | < 500ms |
| `GET /contracts/` | < 1000ms |
| `POST /contracts/` | < 3000ms |
| `POST /genai/analyze-contract` | < 30000ms* |
| `GET /metrics` | < 1000ms |

*GenAI analysis depends on OpenAI API response times

### Throughput Targets
- **Authentication**: 100+ RPS
- **Contract Listing**: 50+ RPS
- **Contract Upload**: 10+ RPS
- **GenAI Analysis**: 5+ RPS (limited by AI service)
- **Health Checks**: 200+ RPS

## Test Data

### Automatic Test Data Generation
The load tests automatically generate:

- **Unique users** for each test run
- **Test clients** for contract association
- **Sample PDF content** for uploads and analysis
- **Realistic contract text** for AI analysis

### Clean Up
Test data is automatically scoped to test users and can be cleaned up by:

1. **Database cleanup** (if needed):
   ```bash
   # Connect to MongoDB and remove test data
   db.users.deleteMany({"username": /^loadtest_user_/})
   db.clients.deleteMany({"name": /^LoadTest Client/})
   db.contracts.deleteMany({"uploaded_by": /^loadtest_user_/})
   ```

2. **Storage cleanup**:
   ```bash
   # Remove test files from storage
   rm -rf storage/contracts/loadtest_*
   ```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure API is running: `docker-compose ps`
   - Check port accessibility: `curl http://localhost:8000/healthz`

2. **High Error Rates**
   - Monitor API logs: `docker-compose logs api`
   - Check database connectivity: `docker-compose logs mongodb`
   - Verify OpenAI API key configuration

3. **Slow Response Times**
   - Monitor system resources: `docker stats`
   - Check database performance
   - Consider scaling workers: `docker-compose up --scale worker=3`

4. **Authentication Failures**
   - Verify JWT token generation
   - Check user registration limits
   - Monitor auth endpoint logs

### Performance Optimization Tips

1. **Database Optimization**
   - Ensure proper indexes are created
   - Monitor connection pool usage
   - Consider read replicas for high read loads

2. **API Optimization**
   - Enable response caching where appropriate
   - Optimize query parameters
   - Consider request rate limiting

3. **Infrastructure Scaling**
   - Scale worker containers for GenAI processing
   - Use load balancers for multiple API instances
   - Consider Redis clustering for high loads

## Integration with CI/CD

### Automated Performance Testing
```yaml
# Example GitHub Actions workflow
- name: Run Load Tests
  run: |
    pip install -r load_tests/requirements.txt
    locust -f load_tests/locustfile.py \
      --host=http://localhost:8000 \
      --users=20 \
      --spawn-rate=2 \
      --run-time=300s \
      --headless \
      --html=performance_report.html \
      --csv=performance_results
```

### Performance Regression Detection
- Set baseline performance metrics
- Fail builds if performance degrades beyond thresholds
- Track performance trends over time

## Reporting

### HTML Reports
Locust generates detailed HTML reports including:
- Response time distributions
- Request rates over time
- Error analysis
- Performance charts

### CSV Data Export
Export raw performance data for analysis:
```bash
--csv=results/performance_test_$(date +%Y%m%d_%H%M%S)
```

### Custom Metrics
The tests can be extended to collect custom metrics:
- Business logic performance
- AI service-specific metrics
- File processing times
- Database query performance