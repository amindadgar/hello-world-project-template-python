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
- MongoDB (included in Docker setup)
- Temporal Server (included in Docker setup)

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd hello-world-project-template-python
```

### 2. Environment Configuration

Copy the environment template and configure your settings:

```bash
cp env.example .env
```

Edit `.env` and set your OpenAI API key:

```bash
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 3. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Start the Full System

```bash
# Start all services (Temporal, MongoDB, Worker, Dashboard)
docker-compose up -d

# Or start individual services
docker-compose up temporal mongodb  # Infrastructure only
```

### 5. Verify System Health

```bash
python scripts/test_system.py
```

This will:
- Test MongoDB connectivity
- Test Temporal server connection
- Create sample data for the dashboard

## 🎯 Usage

### Running the Worker

The worker processes Temporal workflows and activities:

```bash
python run_worker.py
```

### Accessing the Dashboard

The Streamlit dashboard is available at: http://localhost:8501

- **Default password**: `admin123` (configurable via `STREAMLIT_PASSWORD`)
- **Features**:
  - Real-time request monitoring
  - Status filtering (PENDING, RUNNING, COMPLETED, FAILED)
  - Date range filtering
  - Text search in queries and responses
  - Detailed request view with timeline
  - Sentiment analysis results

### Testing Workflows

```bash
python run_workflow.py
```

Choose option 2 to test the HandleTelegramQuery workflow.

### Monitoring Services

- **Temporal Web UI**: http://localhost:8080
- **MongoDB Express**: http://localhost:8081 (admin/password)
- **Streamlit Dashboard**: http://localhost:8501

## 🔧 Development

### Project Structure

```
├── activities.py           # Temporal activities (LLM, logging, sentiment)
├── workflows.py           # Temporal workflows (HandleTelegramQuery)
├── models.py              # Data models and schemas
├── database.py            # MongoDB operations
├── config.py              # Configuration management
├── streamlit_app.py       # Dashboard application
├── run_worker.py          # Worker process
├── run_workflow.py        # Workflow testing
├── docker-compose.yml     # Full system setup
├── scripts/
│   ├── run_dashboard.py   # Dashboard runner
│   └── test_system.py     # System validation
└── mongodb-init/
    └── init.js            # Database initialization
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

#### 3. Streamlit Dashboard Features

- **Authentication**: Simple password protection
- **Real-time Data**: Auto-refreshing request tables
- **Advanced Filtering**: Status, date range, text search
- **Request Details**: Full timeline and enrichment data
- **Responsive Design**: Works on desktop and mobile

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
| `OPENAI_API_KEY` | OpenAI API key | Required |
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

## 🧪 Testing

### Unit Tests

```bash
# Run system validation
python scripts/test_system.py

# Test individual components
python -m pytest tests/  # If you add pytest tests
```

### Manual Testing

1. **Start the system**: `docker-compose up`
2. **Create test data**: `python scripts/test_system.py`
3. **Test workflow**: `python run_workflow.py`
4. **Check dashboard**: Visit http://localhost:8501

## 📊 Monitoring

### Logs

- **Worker logs**: `docker-compose logs worker`
- **Dashboard logs**: `docker-compose logs dashboard`
- **Temporal logs**: `docker-compose logs temporal`

### Metrics

- **Request volume**: Monitor via dashboard
- **Success/failure rates**: Filter by status in dashboard
- **Response times**: Check timestamp differences
- **Error patterns**: Review error messages in failed requests

## 🔒 Security

- **Authentication**: Streamlit dashboard password protection
- **Input validation**: Pydantic models for data validation
- **Rate limiting**: Consider implementing in production
- **API key management**: Store securely, rotate regularly
- **Database access**: Use read-only user for dashboard

## 🚧 Troubleshooting

### Common Issues

1. **"MongoDB connection failed"**
   - Check if MongoDB is running: `docker-compose ps mongodb`
   - Verify connection string in `.env`

2. **"Temporal connection failed"**
   - Check if Temporal is running: `docker-compose ps temporal`
   - Wait for Temporal to fully start (may take 30-60 seconds)

3. **"OpenAI API error"**
   - Verify API key in `.env`
   - Check API quota and usage limits

4. **"Dashboard not loading"**
   - Check if port 8501 is available
   - Verify Streamlit service: `docker-compose logs dashboard`

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python run_worker.py
```

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
2. Review logs for error messages
3. Create an issue in the repository
4. Check Temporal and MongoDB documentation

Happy coding! 🚀
