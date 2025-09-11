---
mode: ask
---
Please code review the code base and provide suggestions for improvement based on the following guidelines:
- Follow Clean Code principles
- Flag long functions and deep nesting
- Use clear, descriptive names
- Check the code execution against the code comments to ensure they align.
- Folow the folloing security best practices:
  - Validate and sanitize all inputs
  - Use parameterized queries to prevent SQL injection
  - Implement proper error handling without exposing sensitive information
  - Ensure secure authentication and authorization mechanisms
  - Use HTTPS for all communications
  - Regularly update dependencies to patch known vulnerabilities
  - Implement logging and monitoring for suspicious activities