# S3 Setup
1. Create an S3 bucket (e.g., ariadne-session-logs).
2. Enable event notifications for `s3:ObjectCreated`.
3. Point event notifications to your classifier Lambda function.
