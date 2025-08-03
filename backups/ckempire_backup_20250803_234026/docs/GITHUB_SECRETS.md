# GitHub Secrets Configuration

This document outlines the required GitHub secrets for the CI/CD pipeline.

## Required Secrets

### AWS Credentials
- `AWS_ACCESS_KEY_ID`: AWS access key for EKS cluster access
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for EKS cluster access
- `AWS_REGION`: AWS region (e.g., us-west-2)
- `EKS_CLUSTER_NAME`: Name of the EKS cluster

### API Keys
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `STRIPE_SECRET_KEY`: Stripe secret key for payment processing

### Database Credentials
- `POSTGRES_PASSWORD`: PostgreSQL database password
- `REDIS_PASSWORD`: Redis password

### Security Keys
- `ENCRYPTION_KEY`: 32-character encryption key for data encryption
- `JWT_SECRET_KEY`: JWT secret key for authentication

## Setting Up Secrets

1. Go to your GitHub repository
2. Navigate to Settings > Secrets and variables > Actions
3. Click "New repository secret"
4. Add each secret with the appropriate name and value

## Security Best Practices

1. **Rotate Keys Regularly**: Update API keys and secrets periodically
2. **Use Environment-Specific Keys**: Use different keys for staging and production
3. **Limit Access**: Only grant necessary permissions to AWS IAM users
4. **Monitor Usage**: Set up alerts for unusual API usage
5. **Encrypt Sensitive Data**: Use base64 encoding for Kubernetes secrets

## Example Secret Values

```bash
# Generate encryption key
openssl rand -base64 32

# Generate JWT secret
openssl rand -base64 32

# Base64 encode passwords
echo -n "your-password" | base64
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Check AWS IAM permissions
2. **Invalid API Key**: Verify OpenAI/Stripe API keys are correct
3. **Connection Timeout**: Check network connectivity and firewall rules
4. **Secret Not Found**: Ensure secrets are properly named in GitHub

### Debugging

1. Check GitHub Actions logs for detailed error messages
2. Verify secret names match exactly in workflow files
3. Test AWS credentials locally with AWS CLI
4. Validate API keys with respective service providers 