import os
import streamlit as st
import requests
import wikipediaapi
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass

# CrewAI imports
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
from crewai_tools import ScrapeWebsiteTool, SerperDevTool

# Pydantic for input validation
from pydantic import BaseModel, Field

# ====================
# CONFIGURATION
# ====================

class AppConfig:
    """Application configuration"""
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")  # OpenWeatherMap API key
    
    @classmethod
    def validate_keys(cls):
        """Validate required API keys"""
        missing_keys = []
        if not cls.GEMINI_API_KEY:
            missing_keys.append("GEMINI_API_KEY")
        if not cls.SERPER_API_KEY:
            missing_keys.append("SERPER_API_KEY")
        if not cls.WEATHER_API_KEY:
            missing_keys.append("WEATHER_API_KEY")
        
        if missing_keys:
            st.error(f"Missing API keys: {', '.join(missing_keys)}")
            st.info("Please set the required environment variables")
            return False
        return True

# ====================
# CUSTOM TOOLS
# ====================

class WeatherToolInput(BaseModel):
    """Input schema for Weather Tool"""
    location: str = Field(..., description="City name or location to get weather for")

class WeatherTool(BaseTool):
    """Custom weather tool using OpenWeatherMap API"""
    name: str = "Weather Information Tool"
    description: str = "Get current weather information for any location"
    args_schema: type[BaseModel] = WeatherToolInput

    def _run(self, location: str) -> str:
        """Fetch weather data from OpenWeatherMap API"""
        try:
            api_key = AppConfig.WEATHER_API_KEY
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            weather_info = f"""
            Weather for {data['name']}, {data['sys']['country']}:
            - Temperature: {data['main']['temp']}°C (feels like {data['main']['feels_like']}°C)
            - Condition: {data['weather'][0]['description'].title()}
            - Humidity: {data['main']['humidity']}%
            - Pressure: {data['main']['pressure']} hPa
            - Wind Speed: {data['wind']['speed']} m/s
            - Visibility: {data.get('visibility', 'N/A')} meters
            """
            
            return weather_info.strip()
        except Exception as e:
            return f"Error fetching weather data: {str(e)}"

class WikipediaToolInput(BaseModel):
    """Input schema for Wikipedia Tool"""
    query: str = Field(..., description="Search query for Wikipedia")

class WikipediaTool(BaseTool):
    """Custom Wikipedia search tool"""
    name: str = "Wikipedia Search Tool"
    description: str = "Search and retrieve information from Wikipedia"
    args_schema: type[BaseModel] = WikipediaToolInput

    def _run(self, query: str) -> str:
        """Search Wikipedia for information"""
        try:
            wiki_wiki = wikipediaapi.Wikipedia('en')
            page = wiki_wiki.page(query)
            
            if page.exists():
                # Get summary (first 500 characters)
                summary = page.summary[:500] + "..." if len(page.summary) > 500 else page.summary
                
                return f"""
                Wikipedia Article: {page.title}
                URL: {page.fullurl}
                
                Summary:
                {summary}
                """
            else:
                # Try searching for pages
                search_results = wiki_wiki.search(query, results=3)
                if search_results:
                    results = "Did you mean:\n"
                    for result in search_results[:3]:
                        results += f"- {result}\n"
                    return results
                else:
                    return f"No Wikipedia articles found for '{query}'"
                    
        except Exception as e:
            return f"Error searching Wikipedia: {str(e)}"

class RAGToolInput(BaseModel):
    """Input schema for RAG Tool"""
    query: str = Field(..., description="Query to search in knowledge base")
    context: str = Field(default="", description="Additional context for the query")

class CustomRAGTool(BaseTool):
    """Simple RAG implementation using web search and context"""
    name: str = "RAG Knowledge Tool"
    description: str = "Retrieval-Augmented Generation tool for enhanced information retrieval"
    args_schema: type[BaseModel] = RAGToolInput

    def _run(self, query: str, context: str = "") -> str:
        """Perform RAG using web search and context augmentation"""
        try:
            # Use Serper for web search
            search_tool = SerperDevTool()
            search_results = search_tool._run(query)
            
            # Combine context with search results
            rag_response = f"""
            RAG Enhanced Response for: {query}
            
            Context: {context if context else "No additional context provided"}
            
            Retrieved Information:
            {search_results}
            
            This information has been retrieved and augmented to provide comprehensive context.
            """
            
            return rag_response.strip()
        except Exception as e:
            return f"Error in RAG processing: {str(e)}"

# ====================
# AGENT DEFINITIONS
# ====================

def setup_llm():
    """Setup Gemini LLM"""
    return LLM(
        model="gemini/gemini-1.5-pro",
        api_key=AppConfig.GEMINI_API_KEY,
        temperature=0.7
    )

def create_agents(llm):
    """Create specialized agents"""
    
    # Manager Agent
    manager_agent = Agent(
        role="AI Task Manager",
        goal="Coordinate and manage tasks across different specialized agents",
        backstory="You are an experienced project manager specialized in AI workflows. "
                 "You understand user requirements and delegate tasks to the most appropriate agents. "
                 "You ensure all agents work together efficiently to provide comprehensive responses.",
        llm=llm,
        allow_delegation=True,
        verbose=True,
        max_iterations=3
    )
    
    # Agent 1: Web Search Agent
    search_agent = Agent(
        role="Web Search Specialist",
        goal="Search the internet for current and relevant information",
        backstory="You are an expert at finding the most relevant and up-to-date information "
                 "from the web using advanced search techniques.",
        tools=[SerperDevTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Agent 2: Web Scraping Agent
    scraping_agent = Agent(
        role="Web Scraping Expert",
        goal="Extract detailed information from specific websites and web pages",
        backstory="You are skilled at extracting and parsing content from websites, "
                 "providing clean and structured information from web sources.",
        tools=[ScrapeWebsiteTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Agent 3: RAG Agent
    rag_agent = Agent(
        role="Knowledge Retrieval Specialist",
        goal="Provide enhanced information using retrieval-augmented generation techniques",
        backstory="You specialize in retrieving relevant information from various sources "
                 "and augmenting it with contextual knowledge to provide comprehensive answers.",
        tools=[CustomRAGTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Agent 4: Weather Agent
    weather_agent = Agent(
        role="Weather Information Specialist",
        goal="Provide accurate and current weather information for any location",
        backstory="You are a meteorological expert who provides detailed weather information "
                 "and forecasts for locations worldwide.",
        tools=[WeatherTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Agent 5: Wikipedia Agent
    wiki_agent = Agent(
        role="Wikipedia Knowledge Expert",
        goal="Retrieve and provide comprehensive information from Wikipedia",
        backstory="You are an expert at finding and presenting relevant information "
                 "from Wikipedia's vast knowledge base.",
        tools=[WikipediaTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    return {
        'manager': manager_agent,
        'search': search_agent,
        'scraping': scraping_agent,
        'rag': rag_agent,
        'weather': weather_agent,
        'wiki': wiki_agent
    }

# ====================
# TASK MANAGEMENT
# ====================

def create_tasks(agents: Dict[str, Agent], user_query: str, task_type: str):
    """Create tasks based on user query and type"""
    
    if task_type == "web_search":
        task = Task(
            description=f"Search the web for information about: {user_query}. "
                       "Provide comprehensive and current information.",
            expected_output="Detailed search results with relevant information and sources",
            agent=agents['search']
        )
        return [task], [agents['search']]
    
    elif task_type == "weather":
        task = Task(
            description=f"Get current weather information for: {user_query}",
            expected_output="Current weather conditions and forecast information",
            agent=agents['weather']
        )
        return [task], [agents['weather']]
    
    elif task_type == "wikipedia":
        task = Task(
            description=f"Find Wikipedia information about: {user_query}",
            expected_output="Comprehensive Wikipedia information with sources",
            agent=agents['wiki']
        )
        return [task], [agents['wiki']]
    
    elif task_type == "comprehensive":
        # Multi-agent comprehensive research
        search_task = Task(
            description=f"Search the web for current information about: {user_query}",
            expected_output="Current web search results and trending information",
            agent=agents['search']
        )
        
        wiki_task = Task(
            description=f"Find detailed Wikipedia information about: {user_query}",
            expected_output="Comprehensive Wikipedia article information",
            agent=agents['wiki']
        )
        
        rag_task = Task(
            description=f"Use RAG to provide enhanced context about: {user_query}. "
                       "Use the context from previous tasks.",
            expected_output="Enhanced information using retrieval-augmented generation",
            agent=agents['rag'],
            context=[search_task, wiki_task]
        )
        
        return [search_task, wiki_task, rag_task], [agents['search'], agents['wiki'], agents['rag']]
    
    else:  # default to manager delegation
        task = Task(
            description=f"Analyze this request and coordinate the appropriate agents to provide "
                       f"a comprehensive response: {user_query}",
            expected_output="Comprehensive response addressing all aspects of the user query",
            agent=agents['manager']
        )
        return [task], [agents['manager']]

# ====================
# STREAMLIT UI
# ====================

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Agentic AI Tool",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Agentic AI Tool")
    st.subheader("Multi-Agent AI System with CrewAI")
    
    # Check API keys
    if not AppConfig.validate_keys():
        st.stop()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        task_type = st.selectbox(
            "Select Task Type",
            ["comprehensive", "web_search", "weather", "wikipedia", "manager_delegation"],
            help="Choose the type of task to perform"
        )
        
        st.subheader("📋 Task Types")
        st.markdown("""
        - **Comprehensive**: Multi-agent research using search, Wikipedia, and RAG
        - **Web Search**: Current information from the internet
        - **Weather**: Current weather conditions for any location
        - **Wikipedia**: Detailed information from Wikipedia
        - **Manager Delegation**: Let the manager decide which agents to use
        """)
        
        # Agent status
        st.subheader("🤖 Available Agents")
        st.markdown("""
        - 🔍 **Web Search Agent**: Internet search
        - 🌐 **Web Scraping Agent**: Website content extraction
        - 🧠 **RAG Agent**: Enhanced information retrieval
        - 🌤️ **Weather Agent**: Weather information
        - 📚 **Wikipedia Agent**: Encyclopedia knowledge
        - 👤 **Manager Agent**: Task coordination
        """)
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Query Input")
        user_query = st.text_area(
            "Enter your query:",
            placeholder="Ask anything... e.g., 'Tell me about artificial intelligence' or 'What's the weather in New York?'",
            height=100
        )
        
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            process_query = st.button("🚀 Process Query", type="primary")
        with col_btn2:
            clear_results = st.button("🗑️ Clear Results")
    
    with col2:
        st.header("📊 System Status")
        
        status_container = st.container()
        with status_container:
            st.success("✅ Gemini API Connected")
            st.success("✅ CrewAI Initialized")
            st.success("✅ All Agents Ready")
            
            if AppConfig.SERPER_API_KEY:
                st.success("✅ Search API Connected")
            else:
                st.warning("⚠️ Search API Not Connected")
                
            if AppConfig.WEATHER_API_KEY:
                st.success("✅ Weather API Connected")
            else:
                st.warning("⚠️ Weather API Not Connected")
    
    # Process query
    if clear_results:
        for key in list(st.session_state.keys()):
            if key.startswith('result_'):
                del st.session_state[key]
        st.rerun()
    
    if process_query and user_query:
        with st.spinner("🔄 Processing your query..."):
            try:
                # Setup LLM and agents
                llm = setup_llm()
                agents = create_agents(llm)
                
                # Create tasks
                tasks, selected_agents = create_tasks(agents, user_query, task_type)
                
                # Create and run crew
                crew = Crew(
                    agents=selected_agents,
                    tasks=tasks,
                    process=Process.sequential,
                    verbose=False,  # Set to False for cleaner UI
                    memory=True
                )
                
                # Execute the crew
                result = crew.kickoff()
                
                # Store result in session state
                st.session_state['result_output'] = result
                st.session_state['result_query'] = user_query
                st.session_state['result_type'] = task_type
                
            except Exception as e:
                st.error(f"Error processing query: {str(e)}")
    
    # Display results
    if 'result_output' in st.session_state:
        st.header("📋 Results")
        
        # Result metadata
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.metric("Query", st.session_state.get('result_query', '')[:30] + "...")
        with col2:
            st.metric("Task Type", st.session_state.get('result_type', '').title())
        with col3:
            st.metric("Timestamp", datetime.now().strftime("%H:%M:%S"))
        
        # Main result
        st.subheader("🎯 AI Response")
        result_container = st.container()
        with result_container:
            st.write(st.session_state['result_output'])
        
        # Download results
        if st.button("💾 Download Results"):
            result_text = f"""
Query: {st.session_state.get('result_query', '')}
Task Type: {st.session_state.get('result_type', '')}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Results:
{st.session_state['result_output']}
            """
            st.download_button(
                label="📄 Download as Text File",
                data=result_text,
                file_name=f"agentic_ai_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()