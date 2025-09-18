# Risk Assessment Backend

A comprehensive Django backend for risk assessment and forecasting with AI-powered analysis and voice interaction capabilities.

## Features

- **REST API**: Complete API for risk data management and analysis
- **Data Ingestion**: Automated data collection from ACLED, World Bank, and media sources
- **NLP Pipeline**: Advanced text processing using ConfliBERT, Falcon, and BLOOM models
- **Forecasting**: Machine learning models with Emerging Trajectories approach
- **Report Generation**: Automated PDF/DOCX report creation with RAG
- **Voice Agent**: Speech-to-text, intent recognition, and conversational AI

## Quick Start

### 1. Setup Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Settings

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 3. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Load Initial Data

```bash
python manage.py shell
```

```python
from api.models import Country, RiskCategory

# Create sample countries
countries = [
    {'name': 'United States', 'iso_code': 'USA', 'region': 'North America'},
    {'name': 'China', 'iso_code': 'CHN', 'region': 'Asia'},
    {'name': 'Germany', 'iso_code': 'DEU', 'region': 'Europe'},
    {'name': 'Brazil', 'iso_code': 'BRA', 'region': 'South America'},
    {'name': 'Nigeria', 'iso_code': 'NGA', 'region': 'Africa'},
]

for country_data in countries:
    Country.objects.get_or_create(**country_data)

# Create risk categories
risk_types = [
    'climate', 'cyber', 'financial', 'geopolitical', 'pandemic',
    'supply-chain', 'energy', 'water', 'food', 'migration',
    'terrorism', 'natural-disaster', 'economic', 'technology', 'social'
]

for risk_type in risk_types:
    RiskCategory.objects.get_or_create(
        risk_type=risk_type,
        defaults={'description': f'{risk_type.replace("-", " ").title()} risk category'}
    )
```

### 5. Start Services

#### Start Redis (for Celery)
```bash
redis-server
```

#### Start Celery Worker
```bash
celery -A risk_assessment_backend worker --loglevel=info
```

#### Start Django Server
```bash
python manage.py runserver
```

## API Endpoints

### Core API (`/api/`)
- `GET /api/countries/` - List countries
- `GET /api/risk-categories/` - List risk categories
- `GET /api/risk-data/` - Get risk data with filtering
- `GET /api/risk-forecasts/` - Get forecasts
- `POST /api/reports/generate/` - Generate reports
- `GET /api/reports/{id}/download/` - Download reports

### NLP Pipeline (`/nlp/`)
- `POST /nlp/process-text/` - Process text through NLP pipeline
- `GET /nlp/analyze-url/` - Analyze content from URL
- `GET /nlp/processed-texts/` - List processed texts
- `GET /nlp/conflict-events/` - List detected conflict events

### Forecasting (`/forecasting/`)
- `POST /forecasting/train-model/` - Train forecasting models
- `POST /forecasting/generate-forecast/` - Generate forecasts
- `GET /forecasting/model-performance/` - Get model metrics

### Voice Agent (`/voice/`)
- `POST /voice/start-session/` - Start voice session
- `POST /voice/process-input/` - Process voice/text input
- `GET /voice/session-history/{id}/` - Get session history

## Data Sources Integration

### ACLED (Armed Conflict Location & Event Data)
1. Register at [ACLED](https://acleddata.com/)
2. Get API key and add to `.env`
3. Run data ingestion: `python manage.py shell -c "from api.tasks import ingest_risk_data; ingest_risk_data.delay()"`

### World Bank Data
1. Get API access (usually free)
2. Add API key to `.env`
3. Data will be automatically ingested

### Media Sources
Configure news APIs and RSS feeds in `api/data_ingestion.py`

## AI Models Setup

### Hugging Face Models
1. Create account at [Hugging Face](https://huggingface.co/)
2. Get access token and add to `.env`
3. Models will be downloaded automatically on first use

### Whisper (Speech-to-Text)
Whisper models are downloaded automatically. For better performance:
- Use `whisper.load_model("medium")` or `"large"`
- Ensure sufficient disk space (models can be 1-3GB)

### Rasa (Optional)
For advanced conversational AI:
1. Install Rasa: `pip install rasa`
2. Initialize Rasa project: `rasa init`
3. Train model: `rasa train`
4. Start Rasa server: `rasa run --enable-api`

## Report Generation

### Generate Report via API
```bash
curl -X POST http://localhost:8000/api/reports/generate/ \
  -H "Content-Type: application/json" \
  -d '{
    "countries": ["United States", "China"],
    "risk_categories": ["climate", "geopolitical"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "forecast_horizon": 90,
    "format": "pdf"
  }'
```

### Download Report
```bash
curl -O http://localhost:8000/api/reports/{report_id}/download/
```

## Voice Interaction

### Start Voice Session
```bash
curl -X POST http://localhost:8000/voice/start-session/
```

### Process Voice Command
```bash
curl -X POST http://localhost:8000/voice/process-input/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "text": "Generate a report for China focusing on climate risks"
  }'
```

## Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
```bash
flake8 .
black .
```

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Production Deployment

### Environment Variables
Set all required environment variables in production:
- `SECRET_KEY`: Strong secret key
- `DEBUG=False`
- Database configuration
- API keys for data sources
- Redis URL for Celery

### Static Files
```bash
python manage.py collectstatic
```

### Process Management
Use supervisord, systemd, or similar to manage:
- Django application server (gunicorn)
- Celery workers
- Redis server

## Troubleshooting

### Common Issues

1. **Model Loading Errors**
   - Ensure sufficient disk space
   - Check internet connection for model downloads
   - Verify Hugging Face token

2. **Data Ingestion Failures**
   - Verify API keys
   - Check rate limits
   - Review logs for specific errors

3. **Voice Processing Issues**
   - Install PyAudio dependencies: `sudo apt-get install portaudio19-dev`
   - Check microphone permissions
   - Verify Whisper model installation

4. **Celery Task Failures**
   - Ensure Redis is running
   - Check Celery worker logs
   - Verify task queue configuration

### Logs
Check Django logs and Celery logs for detailed error information:
```bash
tail -f /path/to/django.log
tail -f /path/to/celery.log
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure code quality checks pass
5. Submit pull request

## License

This project is licensed under the MIT License.