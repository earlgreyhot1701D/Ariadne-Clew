Infrastructure Notes

Objective
Deploy Ariadne Clew as a lightweight, low-cost agent service that any builder can hit with a single API call and view results in a static front-end. The design emphasizes AWS’s customer obsession principle: fast setup, clear documentation, and minimal moving parts.

Architecture (MVP)

S3 + CloudFront – host the static front-end (public/ folder).

API Gateway – public entry point for recap requests.

AWS Lambda – wraps the classifier logic and enforces schema validation.

DynamoDB – optional persistence for session recap objects (session_id, aha_moments, etc.).

Amazon Bedrock – (planned) to generate structured summaries from log text.

Flow

User enters Session ID in the web client.

API Gateway routes /recap requests to Lambda.

Lambda validates input, retrieves data (mock JSON or DynamoDB), and applies classifier logic.

Response returns structured JSON.

Front-end renders Summary or Raw JSON view.

Deployment Steps (MVP)

aws s3 sync public/ s3://YOUR_BUCKET_NAME

Configure CloudFront to serve the S3 bucket with HTTPS.

Create API Gateway REST API with /recap endpoint → Lambda integration.

Deploy Lambda with Python runtime using lambda_classifier.py.

(Optional) Add DynamoDB table Recaps keyed by session_id.

Enable CORS on API Gateway to allow the static site origin.

Cost Considerations

S3 + CloudFront: pennies per month at hackathon scale.

Lambda: pay per request, zero idle cost.

DynamoDB: free tier covers thousands of reads/writes.

Bedrock: usage-based; can be added post-MVP.

Security

All requests go through API Gateway → enforce schema validation.

Enable CloudWatch logs for audit.

IAM roles scoped per service (Lambda, DynamoDB).

Next Steps

Add Bedrock summarization for live log classification.

Integrate CI/CD (GitHub Actions → AWS SAM/CloudFormation).

Expand schema to support project-level aggregation.
