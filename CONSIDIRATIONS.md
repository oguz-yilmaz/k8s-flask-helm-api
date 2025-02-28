# Project Considerations and Limitations

## Development Shortcuts

### Database Configuration
- Used MySQL root user due to having issues with creating new user with Bitnami
MySQL chart, I didn't want to spend more time on this issue.
- **Caution**: Not suitable for production security standards

### Authentication
- Simplified JWT token management

### Rate Limiting
- I used route-based rate limiting instead of creating a global rate limiter

### CI/CD
- Provided GitHub Actions and Argo CD configurations are demonstration examples
- Requires customization for production use

