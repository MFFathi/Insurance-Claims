# Insurance Claims Processing System API Documentation

## Authentication

The API uses JWT (JSON Web Token) authentication. To authenticate:

1. Obtain a token by sending a POST request to `/api/token/`:
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

2. Include the token in subsequent requests in the Authorization header:
```
Authorization: Bearer <your_token>
```

## API Endpoints

### Claims Management

#### 1. Submit Claim
- **Endpoint**: `POST /api/claims/`
- **Authentication**: Required
- **Request Body**:
```json
{
    "policy_number": "POL123456",
    "claim_type": "auto",
    "description": "Accident damage to front bumper",
    "amount": 1500.00,
    "documents": [
        {
            "document_type": "accident_report",
            "file": "<base64_encoded_file>"
        }
    ]
}
```
- **Response**: 201 Created
```json
{
    "id": 1,
    "claim_number": "CLM123456",
    "status": "pending",
    "ml_score": 0.85,
    "ml_confidence": 0.92,
    "ml_recommendation": "approve"
}
```

#### 2. Get Claim Details
- **Endpoint**: `GET /api/claims/{claim_id}/`
- **Authentication**: Required
- **Response**: 200 OK
```json
{
    "id": 1,
    "claim_number": "CLM123456",
    "policy_number": "POL123456",
    "claim_type": "auto",
    "description": "Accident damage to front bumper",
    "amount": 1500.00,
    "status": "pending",
    "submission_date": "2024-02-20T10:30:00Z",
    "ml_score": 0.85,
    "ml_confidence": 0.92,
    "ml_recommendation": "approve",
    "documents": [
        {
            "id": 1,
            "document_type": "accident_report",
            "upload_date": "2024-02-20T10:30:00Z",
            "status": "verified"
        }
    ]
}
```

### ML Model Management

#### 1. Get Model Status
- **Endpoint**: `GET /api/ml/models/`
- **Authentication**: Required (Admin only)
- **Response**: 200 OK
```json
{
    "models": [
        {
            "id": 1,
            "name": "fraud_detection",
            "version": "1.0.0",
            "status": "active",
            "performance_metrics": {
                "accuracy": 0.95,
                "precision": 0.94,
                "recall": 0.93
            }
        }
    ]
}
```

#### 2. Retrain Model
- **Endpoint**: `POST /api/ml/models/retrain/`
- **Authentication**: Required (Admin only)
- **Request Body**:
```json
{
    "model_type": "fraud_detection",
    "parameters": {
        "n_neighbors": 5,
        "weights": "uniform"
    }
}
```
- **Response**: 202 Accepted
```json
{
    "task_id": "retrain_123",
    "status": "started",
    "estimated_completion": "2024-02-20T11:30:00Z"
}
```

### Document Management

#### 1. Upload Document
- **Endpoint**: `POST /api/claims/{claim_id}/documents/`
- **Authentication**: Required
- **Request Body**: multipart/form-data
```
document_type: accident_report
file: <file>
```
- **Response**: 201 Created
```json
{
    "id": 1,
    "document_type": "accident_report",
    "upload_date": "2024-02-20T10:30:00Z",
    "status": "pending"
}
```

## Error Handling

The API uses standard HTTP status codes and returns error responses in the following format:

```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable error message",
        "details": {
            "field_name": ["Specific error message"]
        }
    }
}
```

Common error codes:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Best Practices

1. Always include the JWT token in the Authorization header
2. Handle rate limiting by implementing exponential backoff
3. Validate request data before sending
4. Handle errors gracefully
5. Use appropriate HTTP methods for each operation
6. Keep sensitive data secure
7. Monitor API usage and performance

## Security Considerations

1. All API endpoints require authentication
2. Sensitive data is encrypted in transit (HTTPS)
3. File uploads are validated and scanned
4. Rate limiting is implemented to prevent abuse
5. Input validation is performed on all endpoints
6. Access control is enforced at both API and data levels