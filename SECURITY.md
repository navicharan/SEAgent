# Security Configuration Guide

## Environment Variables Setup

### Required Environment Variables

1. **OpenAI API Key** (Required for AI features)
   ```bash
   OPENAI_API_KEY=sk-your-actual-openai-api-key-here
   ```

2. **Secret Key** (Required for security)
   ```bash
   SECRET_KEY=your-unique-secret-key-here
   ```

### Optional Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=sqlite:///seagent.db
DATABASE_ECHO=false

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Logging
LOG_LEVEL=INFO

# Environment
ENVIRONMENT=development
DEBUG=true
```

## Setup Instructions

### 1. Create .env file
```bash
cp .env.example .env
```

### 2. Edit .env file with your actual values
```bash
# Edit the .env file and add your actual API keys
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
SECRET_KEY=$(openssl rand -base64 32)  # Generate a secure secret
```

### 3. Verify .env is in .gitignore
The `.env` file should never be committed to version control. Ensure it's listed in `.gitignore`.

## Security Best Practices

### ✅ DO
- Use environment variables for all sensitive data
- Generate strong, unique secret keys
- Regularly rotate API keys
- Use HTTPS in production
- Set strong CORS policies for production
- Monitor API usage and logs

### ❌ DON'T
- Commit .env files to version control
- Use default secret keys in production
- Share API keys in plain text
- Use development settings in production
- Log sensitive information

## Production Deployment

### Environment Variables for Production
```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secure-secret-key
OPENAI_API_KEY=your-production-openai-key
API_HOST=0.0.0.0
LOG_LEVEL=WARNING
```

### Additional Security Measures
1. **Firewall Configuration**: Restrict access to necessary ports only
2. **SSL/TLS**: Use HTTPS certificates
3. **Rate Limiting**: Configure appropriate rate limits
4. **Monitoring**: Set up logging and monitoring
5. **Backup**: Regular backups of configuration and data

## Troubleshooting

### OpenAI Not Working
- Check if `OPENAI_API_KEY` is set correctly
- Verify the API key starts with `sk-`
- Check OpenAI account has sufficient credits
- Look for error messages in logs

### Configuration Issues
- Verify .env file exists and is readable
- Check environment variable names are correct
- Restart application after changing .env file
- Use `printenv | grep -i openai` to verify environment loading

## Security Verification

Run the application and check for these security indicators:

✅ **Good Signs:**
- "Loading environment variables from .env" message
- "OpenAI client initialized successfully" (if API key is valid)
- No hardcoded secrets in logs

⚠️ **Warning Signs:**
- "Using default secret key" warning
- "OpenAI API key not found" (if you intended to use OpenAI)
- Sensitive data appearing in logs or error messages
