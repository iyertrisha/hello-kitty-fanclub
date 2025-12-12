# SendGrid Setup Instructions

## Configuration

To use the email OTP functionality, you need to configure your SendGrid API key.

### Steps:

1. Copy the environment template:
   ```bash
   cp env.template .env
   ```

2. Add your SendGrid API key to the `.env` file:
   ```
   SENDGRID_API_KEY=SG.your_api_key_here
   SENDGRID_FROM_EMAIL=noreply@yourdomain.com
   ```

3. Make sure your SendGrid account has a verified sender email address for `SENDGRID_FROM_EMAIL`.

4. Restart your Flask server for changes to take effect.

## Testing

After setup, test the OTP flow:
1. Navigate to the supplier portal login page
2. Enter an email address
3. Check your email for the OTP code
4. Enter the OTP to complete login

## Notes

- OTP codes expire after 10 minutes
- Rate limiting: Maximum 3 OTP requests per email per 15 minutes
- OTPs are one-time use only

