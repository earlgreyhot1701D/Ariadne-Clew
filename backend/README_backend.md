# Ariadne Backend

## API Endpoint

### Recap Endpoint

```
GET /recap?session_id=abc123
```

### Example cURL

```bash
curl -X GET "http://localhost:5000/recap?session_id=example123"
```

## CORS Setup

Ensure your Flask app includes:

```python
from flask_cors import CORS
CORS(app)
```

This allows frontend access during local dev or from Vercel/Netlify deployment.

## Running

```bash
pip install -r requirements.txt
python app.py
```

## Testing

```bash
pytest
```
