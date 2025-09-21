# Agentic AI Tool - Complete Setup and Deployment Guide

## 🎯 Overview

This is a production-ready agentic AI tool built with CrewAI that combines multiple specialized agents:

- **Agent 1**: Web Search Agent (using SerperDev)
- **Agent 2**: Web Scraping Agent (using built-in CrewAI tools)
- **Agent 3**: RAG Agent (Retrieval-Augmented Generation)
- **Agent 4**: Weather Agent (using OpenWeatherMap API)
- **Agent 5**: Wikipedia Agent (using Wikipedia API)
- **Manager Agent**: Coordinates and delegates tasks to appropriate agents

## 🏗️ Architecture

```
User Input → Streamlit UI → Manager Agent → Specialized Agents → Results
```

### Key Features:
- ✅ Gemini API integration through Google API
- ✅ Built-in CrewAI tools (web scraping, search)
- ✅ Custom tools (weather, Wikipedia, RAG)
- ✅ Manager agent for intelligent task delegation
- ✅ Production-ready with Docker deployment
- ✅ Streamlit UI for user interaction
- ✅ Health checks and monitoring
- ✅ Environment-based configuration

## 🚀 Quick Start

### Prerequisites

1. **API Keys Required:**
   - Google Gemini API key
   - Serper API key (for web search)
   - OpenWeatherMap API key (for weather data)

2. **System Requirements:**
   - Python 3.11+
   - Docker & Docker Compose
   - 4GB+ RAM

### Setup Instructions

1. **Clone and Setup:**
   ```bash
   # Create project directory
   mkdir agentic-ai-tool
   cd agentic-ai-tool
   
   # Copy all the provided files to this directory
   ```

2. **Configure Environment:**
   ```bash
   # Copy environment template
   cp .env.template .env
   
   # Edit .env file with your API keys
   nano .env
   ```

3. **API Key Setup:**
   
   **Gemini API Key:**
   - Visit: https://ai.google.dev/
   - Create account and get API key
   - Add to .env: `GEMINI_API_KEY=your_key_here`
   
   **Serper API Key:**
   - Visit: https://serper.dev/
   - Sign up and get API key
   - Add to .env: `SERPER_API_KEY=your_key_here`
   
   **Weather API Key:**
   - Visit: https://openweathermap.org/api
   - Create account and get API key
   - Add to .env: `WEATHER_API_KEY=your_key_here`

## 🐳 Production Deployment

### Option 1: Docker Compose (Recommended)

```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### Option 2: Manual Docker

```bash
# Build image
docker build -t agentic-ai-tool .

# Run container
docker run -d \
  --name agentic-ai-tool \
  -p 8501:8501 \
  --env-file .env \
  agentic-ai-tool
```

### Option 3: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run agentic_ai_tool.py
```

## 🎛️ Application Features

### Task Types Available:

1. **Comprehensive Research**: Multi-agent collaboration using search, Wikipedia, and RAG
2. **Web Search**: Real-time internet search for current information
3. **Weather Information**: Current weather conditions for any location
4. **Wikipedia Research**: Detailed encyclopedia information
5. **Manager Delegation**: Intelligent task routing by manager agent

### Agent Capabilities:

**Manager Agent:**
- Coordinates task distribution
- Delegates to appropriate specialists
- Synthesizes multi-agent results

**Web Search Agent:**
- Real-time internet search
- Current news and trends
- Authoritative source identification

**Web Scraping Agent:**
- Website content extraction
- Structured data retrieval
- Clean content parsing

**RAG Agent:**
- Knowledge augmentation
- Context-aware responses
- Multi-source information synthesis

**Weather Agent:**
- Global weather data
- Detailed meteorological information
- Real-time conditions

**Wikipedia Agent:**
- Comprehensive encyclopedia search
- Article summaries and links
- Related topic suggestions

## 🔧 Configuration

### Environment Variables:
```bash
GEMINI_API_KEY=your_gemini_api_key
SERPER_API_KEY=your_serper_api_key
WEATHER_API_KEY=your_weather_api_key
PYTHONUNBUFFERED=1
STREAMLIT_SERVER_PORT=8501
```

### YAML Configuration:
- `config_agents.yaml`: Agent definitions and roles
- `config_tasks.yaml`: Task templates and workflows

## 📊 Monitoring & Health Checks

- **Health Endpoint**: `http://localhost:8501/_stcore/health`
- **Application URL**: `http://localhost:8501`
- **Docker Logs**: `docker-compose logs -f`

## 🛠️ Maintenance Commands

```bash
# View logs
docker-compose logs -f

# Stop application
docker-compose down

# Restart application
docker-compose restart

# Update and redeploy
docker-compose pull && docker-compose up -d

# Scale application (if needed)
docker-compose up -d --scale agentic-ai-tool=3
```

## 🔒 Security Features

- Non-root user in Docker container
- Environment variable protection
- Input validation with Pydantic
- Error handling and logging
- Health check monitoring

## 📈 Production Considerations

### Scaling:
- Use container orchestration (Kubernetes)
- Implement load balancing
- Add Redis for caching
- Use managed databases for persistence

### Monitoring:
- Add application performance monitoring
- Implement logging aggregation
- Set up alerting for failures
- Monitor API rate limits

### Security:
- Use secrets management
- Implement authentication
- Add rate limiting
- Enable HTTPS/TLS

## 🚨 Troubleshooting

### Common Issues:

1. **API Key Errors:**
   - Verify all API keys are set correctly
   - Check API quotas and limits
   - Ensure network connectivity

2. **Docker Issues:**
   - Check Docker daemon is running
   - Verify port 8501 is available
   - Check system resources

3. **Application Errors:**
   - Review logs: `docker-compose logs`
   - Check environment variables
   - Verify dependencies

### Support:
- Check logs for detailed error messages
- Verify API key validity and quotas
- Ensure all required files are present
- Test individual components

## 📚 Usage Examples

### Example Queries:

1. **Comprehensive Research:**
   - "Tell me about artificial intelligence trends in 2025"
   - "Research quantum computing applications"

2. **Weather Information:**
   - "Weather in New York"
   - "Current conditions in Tokyo"

3. **Wikipedia Research:**
   - "Information about machine learning"
   - "History of space exploration"

4. **Web Search:**
   - "Latest AI developments"
   - "Current technology trends"

Once deployed, the agentic AI tool will be available at `http://localhost:8501` with a Streamlit interface allowing users to interact with multiple specialized AI agents through a single, unified system.