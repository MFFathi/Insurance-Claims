# Insurance Claims Processing System

A comprehensive Django-based system for processing and managing insurance claims, incorporating machine learning for claim analysis and automated decision-making.

## Project Overview

This project is a full-stack insurance claims processing system that includes:
- Customer-facing portal for claim submission
- Administrative interface for claim management
- Machine learning models for claim analysis
- RESTful API for system integration
- Automated claim processing and decision-making

## System Architecture

The project is organized into several key components:
- `InsuranceClaimsCustomer/`: Customer-facing web interface
- `InsuranceClaimsUser/`: Administrative interface
- `InsuranceClaimsML/`: Machine learning models and analysis
- `InsuranceClaimsAPI/`: REST API endpoints
- `InsuranceClaimsRecords/`: Database models and data management

## Machine Learning Models

The system uses K-Nearest Neighbors (KNN) models for claim analysis and prediction. Key features:

- Multiple model versions (0.1 to 0.4) for A/B testing and performance comparison
- Model accuracy tracking and versioning
- Automatic model selection based on performance
- Support for model retraining and updates

### Model Features
- Claim amount prediction
- Fraud detection
- Risk assessment
- Processing time estimation

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- PostgreSQL
- Git
- scikit-learn 1.4.2
- pandas 2.2.2

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd Insurance-Claims
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@localhost:5432/insurance_claims
ML_MODEL_PATH=/path/to/ml_models
```

5. Run database migrations:
```bash
python manage.py migrate
```

## Running the Application

### Development Mode
```bash
python manage.py runserver
```

### Using Docker
```bash
docker-compose up --build
```

### Running Tests
```bash
pytest
```

## Project Structure

```
Insurance-Claims/
├── InsuranceClaimsCustomer/     # Customer portal
├── InsuranceClaimsUser/         # Admin interface
├── InsuranceClaimsML/           # ML models
│   ├── models.py               # ML model definitions
│   ├── views.py               # ML endpoints
│   └── tests.py               # ML model tests
├── InsuranceClaimsAPI/          # API endpoints
├── InsuranceClaimsRecords/      # Database models
├── MLModel/                     # Trained ML models
├── tests/                       # Test suite
├── templates/                   # HTML templates
└── staticfiles/                 # Static assets
```

## API Documentation

The API documentation is available at `/api/docs/` when running the development server.

### Key API Endpoints

- `/api/claims/` - Claim submission and management
- `/api/ml/predict/` - ML model predictions
- `/api/ml/models/` - ML model management
- `/api/users/` - User management

## Deployment

### Production Setup
1. Set up a PostgreSQL database
2. Configure environment variables for production
3. Set up a reverse proxy (Nginx recommended)
4. Configure SSL certificates
5. Set up monitoring and logging

### Docker Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write tests for new features
- Update documentation
- Use meaningful commit messages

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact [support-email] or create an issue in the repository.

## Acknowledgments

- Django Framework
- scikit-learn
- PostgreSQL
- Docker
