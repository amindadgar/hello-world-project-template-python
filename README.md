# AI Agent with Temporal Orchestration, MongoDB Logging, and Streamlit UI

A comprehensive AI-driven agent system that processes Telegram messages through Temporal workflows, logs everything to MongoDB, and provides a beautiful Streamlit dashboard for monitoring and administration.

## 🚀 Features

- **Temporal Orchestration**: Reliable workflow execution with built-in retry policies and error handling
- **MongoDB Logging**: Complete audit trail of all requests and responses
- **Streamlit Dashboard**: Real-time monitoring and filtering of request logs
- **LLM Integration**: OpenAI GPT-4o-mini for concise responses
- **Sentiment Analysis**: Optional enrichment of responses
- **Telegram Integration**: Ready for n8n workflow integration
- **Docker Support**: Complete containerized development environment

## 🏗️ System Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Telegram  │    │     n8n     │    │  Temporal   │    │  MongoDB    │
│  (Messages) │───▶│ (Workflow)  │───▶│ (Workflow)  │───▶│ (Logging)   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                             │
                                             ▼
                                   ┌─────────────┐
                                   │   OpenAI    │
                                   │    (LLM)    │
                                   └─────────────┘
                                             │
                                             ▼
                                   ┌─────────────┐
                                   │  Streamlit  │
                                   │ (Dashboard) │
                                   └─────────────┘
```

## 📋 Requirements

- Python 3.8+
- Docker and Docker Compose
- OpenAI API Key
- 4GB+ RAM (for running all services)

## 🛠️ Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd hello-world-project-template-python

# 2. Run the automated setup script
./scripts/start_system.sh
```

The script will:
- Create `.env` file from template
- Build and start all Docker services
- Check service health
- Display service URLs and commands

### Option 2: Manual Setup

#### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd hello-world-project-template-python
```

#### 2. Environment Configuration

```bash
cp env.template .env
```

Edit `.env` and set your OpenAI API key:

```bash
OPENAI_API_KEY=your_actual_openai_api_key_here
```

#### 3. Start All Services

```bash
# Start the complete system
docker-compose up -d

# View logs
docker-compose logs -f
```

#### 4. Verify System Health

```bash
python scripts/test_system.py
```

## 🎯 Usage

### 🌐 Accessing Services

Once started, the following services are available:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Streamlit Dashboard** | http://localhost:8501 | Password: `admin123` |
| **Temporal Web UI** | http://localhost:8080 | No auth required |
| **MongoDB Express** | http://localhost:8081 | admin/password |

### 🔧 Development Commands

```bash
# Start system
docker-compose up -d

# Stop system  
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart worker

# Run tests
python scripts/test_system.py

# Test workflow locally
python run_workflow.py
```

### 📊 Dashboard Features

The Streamlit dashboard provides:
- **Real-time request monitoring**
- **Status filtering** (PENDING, RUNNING, COMPLETED, FAILED)
- **Date range filtering**
- **Text search** in queries and responses
- **Detailed request view** with complete timeline
- **Sentiment analysis** results display
- **Auto-refresh** capabilities

### 🧪 Testing Workflows

```bash
# Interactive workflow testing
python run_workflow.py

# System health check with sample data
python scripts/test_system.py

# Run dashboard locally (outside Docker)
python scripts/run_dashboard.py
```

## 🔧 Development

### Project Structure

```
├── activities.py               # Temporal activities (LLM, logging, sentiment)
├── workflows.py               # Temporal workflows (HandleTelegramQuery)
├── models.py                  # Data models and schemas
├── database.py                # MongoDB operations
├── config.py                  # Configuration management
├── streamlit_app.py           # Dashboard application
├── run_worker.py              # Worker process
├── run_workflow.py            # Workflow testing
├── Dockerfile                 # Multi-stage Docker build
├── docker-compose.yml         # Complete system orchestration
├── env.template               # Environment variables template
├── dynamicconfig/             # Temporal server configuration
├── mongodb-init/              # MongoDB initialization scripts
└── scripts/
    ├── start_system.sh        # System startup script
    ├── run_dashboard.py       # Dashboard runner
    └── test_system.py         # System validation
```

### Key Components

#### 1. Temporal Workflow (`HandleTelegramQuery`)

The main workflow orchestrates:
1. **Log Initial Request**: Store request in MongoDB with PENDING status
2. **Invoke LLM**: Call OpenAI API with retry logic
3. **Update Result**: Store response and mark COMPLETED
4. **Sentiment Analysis**: Optional enrichment step
5. **Return Result**: Provide result for n8n consumption

#### 2. MongoDB Schema

```javascript
{
  "request_id": "uuid",
  "workflow_instance_id": "temporal-workflow-id",
  "chat_id": "telegram-chat-id", 
  "user_id": 265278326,
  "query_text": "User's message",
  "timestamp_received": "ISO8601",
  "timestamp_logged": "ISO8601",
  "status": "PENDING|RUNNING|COMPLETED|FAILED",
  "answer_text": "AI response",
  "timestamp_answered": "ISO8601",
  "sentiment_score": 0.8,
  "sentiment_label": "Positive",
  "error_message": null
}
```

#### 3. Docker Services

| Service | Purpose | Port |
|---------|---------|------|
| `temporal` | Workflow orchestration server | 7233, 8080 |
| `postgresql` | Temporal's database | 5432 |
| `mongodb` | AI agent data storage | 27017 |
| `worker` | Temporal worker (AI agent) | - |
| `dashboard` | Streamlit UI | 8501 |
| `mongo-express` | MongoDB web UI | 8081 |

## 🔗 n8n Integration

### Telegram Trigger → Temporal Workflow

```json
{
  "requestId": "<UUID>",
  "chatId": "<telegramChatId>", 
  "userId": 265278326,
  "queryText": "<message.text>",
  "timestampReceived": "<ISO8601>"
}
```

### Getting Workflow Results

n8n can poll for results using the workflow instance ID:

```javascript
// Pseudo-code for n8n
const workflowId = "telegram-query-" + requestId;
const result = await temporal.getWorkflowResult(workflowId);
// result.answerText contains the AI response
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TEMPORAL_HOST` | Temporal server address | `localhost:7233` |
| `TEMPORAL_TASK_QUEUE` | Task queue name | `telegram-agent-queue` |
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `OPENAI_API_KEY` | OpenAI API key | **Required** |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o-mini` |
| `AUTHORIZED_USER_ID` | Telegram user ID filter | `265278326` |
| `STREAMLIT_PASSWORD` | Dashboard password | `admin123` |
| `SENTIMENT_API_ENABLED` | Enable sentiment analysis | `false` |
| `LLM_RETRY_ATTEMPTS` | Max LLM retry attempts | `3` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Production Deployment

For production deployment:

1. **Use Temporal Cloud** or self-hosted cluster
2. **Use MongoDB Atlas** or managed MongoDB
3. **Set strong passwords** for all services
4. **Enable TLS** for all connections
5. **Use environment-specific configs**
6. **Scale worker instances** as needed

## 🧪 Testing

### Automated Testing

```bash
# Complete system test with sample data
python scripts/test_system.py

# Docker health check
docker-compose ps

# Service connectivity test
./scripts/start_system.sh --check
```

### Manual Testing

1. **Start the system**: `./scripts/start_system.sh`
2. **Visit dashboard**: http://localhost:8501 (password: admin123)
3. **Test workflow**: `python run_workflow.py`
4. **Check Temporal UI**: http://localhost:8080

## 📊 Monitoring

### Service Health

```bash
# Check all services
docker-compose ps

# View logs for specific service
docker-compose logs -f worker
docker-compose logs -f dashboard
docker-compose logs -f temporal

# Monitor resource usage
docker stats
```

### Application Metrics

- **Request volume**: Monitor via dashboard
- **Success/failure rates**: Filter by status in dashboard
- **Response times**: Check timestamp differences
- **Error patterns**: Review error messages in failed requests

## 🔒 Security

- **Authentication**: Streamlit dashboard password protection
- **Input validation**: Pydantic models for data validation
- **Network isolation**: Docker networks
- **Non-root containers**: Security-focused Dockerfile
- **Environment variables**: Sensitive data in .env files

## 🚧 Troubleshooting

### Common Issues

1. **"Services not starting"**
   - Ensure Docker has sufficient memory (4GB+)
   - Check if ports are available: `netstat -tulpn | grep :8080`

2. **"MongoDB connection failed"**
   - Wait for MongoDB to fully initialize (30-60 seconds)
   - Check logs: `docker-compose logs mongodb`

3. **"Temporal connection failed"**
   - Temporal needs time to start (60-90 seconds)
   - Check logs: `docker-compose logs temporal`

4. **"OpenAI API error"**
   - Verify API key in `.env` file
   - Check API quota and usage limits

5. **"Dashboard not loading"**
   - Ensure port 8501 is available
   - Check logs: `docker-compose logs dashboard`

6. **"Pydantic errors"**
   - The system uses Pydantic v2
   - Run `pip install --upgrade pydantic` if needed

### Debug Commands

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Restart with fresh data
docker-compose down -v
docker-compose up -d

# Enter container for debugging
docker-compose exec worker bash
docker-compose exec dashboard bash
```

## 🚀 Performance Tips

1. **Resource Allocation**: Ensure Docker has at least 4GB RAM
2. **Database Indexing**: Indexes are created automatically
3. **Caching**: Streamlit uses 60-second caching
4. **Scaling**: Scale worker instances with `docker-compose up --scale worker=3`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Temporal**: For reliable workflow orchestration
- **OpenAI**: For powerful language models
- **Streamlit**: For rapid dashboard development
- **MongoDB**: For flexible document storage

---

## 📞 Support

For questions or issues:

1. Check the troubleshooting section above
2. Review logs: `docker-compose logs -f`
3. Run health check: `python scripts/test_system.py`
4. Create an issue in the repository

Happy coding! 🚀
