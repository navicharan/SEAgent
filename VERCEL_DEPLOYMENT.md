# Vercel Deployment Guide for SEAgent

## Changes Made for Vercel Compatibility

### 1. **api/app.py** - Serverless Entrypoint
- ✅ Lazy initialization to avoid cold start timeouts
- ✅ Middleware-based initialization on first request
- ✅ Prevents concurrent initialization attempts
- ✅ No startup event hooks (not compatible with serverless)

### 2. **orchestrator/agent_coordinator.py** - Coordinator Improvements
- ✅ Added `initialized` flag to track state
- ✅ Skips background loops in serverless environments
- ✅ Detects VERCEL and AWS_LAMBDA_FUNCTION_NAME environment variables
- ✅ Prevents duplicate agent initialization

### 3. **agents/application_generator_agent.py** - File System Compatibility
- ✅ Uses `/tmp` directory in serverless environments
- ✅ Falls back to system temp directory for local development
- ✅ Properly handles read-only filesystem restrictions

### 4. **pyproject.toml** - Package Configuration
- ✅ Explicitly defines packages to include
- ✅ Lists all dependencies inline
- ✅ Removed UI package (not needed for API)
- ✅ Includes package data (JSON, YAML, HTML)

### 5. **requirements-vercel.txt** - Optimized Dependencies
- ✅ Core FastAPI dependencies only
- ✅ Removed heavy ML libraries (pandas, numpy, scikit-learn)
- ✅ Removed development tools (pytest, black, mypy)
- ✅ Removed incompatible packages (docker, redis, celery, streamlit)
- ✅ Kept essential AI clients (openai, PyGithub)

### 6. **vercel.json** - Deployment Configuration
- ✅ Points to `api/app.py` as entrypoint
- ✅ Sets `maxDuration` to 60 seconds (Pro plan required)
- ✅ Sets `maxLambdaSize` to 50mb
- ✅ Adds VERCEL=1 environment variable
- ✅ Proper routing configuration

### 7. **.vercelignore** - Exclude Unnecessary Files
- ✅ Excludes tests, docs, examples
- ✅ Excludes Docker files
- ✅ Excludes .github workflows
- ✅ Excludes large datasets
- ✅ Reduces deployment size significantly

## Deployment Steps

### 1. Set Environment Variables in Vercel Dashboard

Required:
```
OPENAI_API_KEY=your_openai_api_key_here
```

Optional:
```
GITHUB_TOKEN=your_github_token_here
DEEPSEEK_API_KEY=your_deepseek_key_here
OPENAI_MODEL=gpt-4
ENVIRONMENT=production
```

### 2. Deploy to Vercel

```bash
# Commit all changes
git add .
git commit -m "Configure for Vercel deployment"
git push

# Vercel will automatically deploy from your GitHub repository
```

Or use Vercel CLI:
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

### 3. Verify Deployment

After deployment, test the API:

```bash
# Health check
curl https://your-app.vercel.app/health

# API documentation
open https://your-app.vercel.app/docs

# Test code generation
curl -X POST https://your-app.vercel.app/api/v1/generate/direct \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Create a Python function to calculate fibonacci numbers",
    "language": "python"
  }'
```

## Important Notes

### Limitations on Vercel

1. **Execution Timeout**:
   - Hobby Plan: 10 seconds
   - Pro Plan: 60 seconds (configured in vercel.json)
   - Code generation may timeout for complex requests

2. **Memory Limits**:
   - Hobby Plan: 1024 MB
   - Pro Plan: 3008 MB
   - Large model operations may hit memory limits

3. **File System**:
   - Read-only except `/tmp` (500 MB limit)
   - Files in `/tmp` are cleared between cold starts
   - Don't persist data to filesystem

4. **Background Processes**:
   - No background workers (Celery, Redis not supported)
   - Each request is isolated
   - Use external queue services if needed

### Recommended Production Setup

For production workloads with:
- Long-running code generation (>60s)
- Large model operations
- Persistent storage needs
- Background task processing

Consider deploying to:
- **Railway** (better for long-running processes)
- **Render** (includes persistent disk)
- **AWS Lambda** with extended timeout
- **Google Cloud Run** (up to 60 minutes timeout)
- **DigitalOcean App Platform**

### Alternative: Hybrid Deployment

Keep Vercel for:
- API endpoints
- Dashboard UI
- Quick operations

Deploy to separate service for:
- Code generation
- Security analysis
- CI/CD operations

Connect via HTTP API calls between services.

## Troubleshooting

### Build Fails with "Multiple top-level packages"
✅ Fixed in pyproject.toml with explicit package list

### Runtime Error: "No such file or directory"
✅ Fixed by using `/tmp` directory in serverless environments

### Timeout During Code Generation
- Use Pro plan for 60s timeout
- Optimize prompts to be more specific
- Consider breaking into smaller requests
- Use background queue service for long operations

### Import Errors
✅ All heavy dependencies removed from requirements-vercel.txt

### Cold Start Issues
✅ Lazy initialization prevents timeout during cold starts

## Monitoring

Monitor your deployment:
1. Vercel Dashboard: https://vercel.com/dashboard
2. Function Logs: Check execution logs for errors
3. Analytics: Monitor request patterns and failures

## Cost Estimation

**Hobby Plan** (Free):
- 100 GB-hours per month
- 100 requests per day
- 10s timeout
- Good for: Testing, demos, low traffic

**Pro Plan** ($20/month):
- 1000 GB-hours per month
- Unlimited requests
- 60s timeout
- Good for: Production API, moderate traffic

## Support

For issues:
1. Check Vercel logs for errors
2. Verify environment variables are set
3. Test locally first: `python main.py`
4. Check GitHub Issues: https://github.com/navicharan/SEAgent/issues
