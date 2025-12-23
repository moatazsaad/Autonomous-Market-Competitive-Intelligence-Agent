from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pydantic import BaseModel, Field
from crewai_tools import SerperDevTool
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage

class MarketCompany(BaseModel):
    """A company identified during market scanning"""
    name: str = Field(description="Company name")
    ticker: str = Field(description="Stock ticker symbol")
    reason: str = Field(description="Reason company is trending")

class MarketScanResult(BaseModel):
    """Result of collecting market data for trending companies"""
    companies: List[MarketCompany] = Field(description="List of trending companies")


class CompetitorProfile(BaseModel):
    """Detailed competitor analysis for a company"""
    name: str = Field(description="Company name")
    market_position: str = Field(description="Current market position and competitive analysis")
    future_outlook: str = Field(description="Future outlook and growth prospects")
    investment_potential: str = Field(description="Investment potential and suitability for investment")

class CompetitorAnalysisResult(BaseModel):
    """Aggregated competitor analysis output"""
    research_list: List[CompetitorProfile] = Field(description="List of competitor profiles with analysis")


class StrategyReport(BaseModel):
    """Structured strategic report generated for executives"""
    summary: str = Field(description="Executive summary of findings")
    trends: str = Field(description="Key market trends")
    opportunities: str = Field(description="Opportunities identified")
    risks: str = Field(description="Risks identified")
    recommendations: str = Field(description="Actionable recommendations")

@CrewBase
class AutonomousMarketIntelligence():
    """AutonomousMarketIntelligence crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'


    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], 
            tools=[SerperDevTool()],
            verbose=True
        )

    @agent
    def competitor_analyzer(self) -> Agent:
        return Agent(config=self.agents_config['competitor_analyzer'], verbose=True)

    @agent
    def strategy_synthesizer(self) -> Agent:
        return Agent(config=self.agents_config['strategy_synthesizer'], verbose=True)

 


    @task
    def collect_market_data_task(self) -> Task:
        return Task(config=self.tasks_config['collect_market_data_task'],
            output_pydantic=MarketScanResult)

    @task
    def analyze_competitors_task(self) -> Task:
        return Task(config=self.tasks_config['analyze_competitors_task'],
            output_pydantic=CompetitorAnalysisResult)

    @task
    def generate_strategy_report_task(self) -> Task:
        return Task(config=self.tasks_config['generate_strategy_report_task'],
            output_pydantic=StrategyReport)




    @crew
    def crew(self) -> Crew:
        """Creates the AutonomousMarketIntelligence crew"""

        manager = Agent(
            config=self.agents_config['manager'],
            allow_delegation=True,
            verbose=True
        )

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.hierarchical,
            verbose=True,
            memory=True,
            manager_agent=manager,
            long_term_memory = LongTermMemory(
                storage=LTMSQLiteStorage(
                    db_path="./memory/long_term_memory_storage.db"
                )
            ),
            # Short-term memory for current context using RAG
            short_term_memory = ShortTermMemory(
                storage = RAGStorage(
                        embedder_config={
                            "provider": "openai",
                            "config": {
                                "model": 'text-embedding-3-small'
                            }
                        },
                        type="short_term",
                        path="./memory/"
                    )
                ),            # Entity memory for tracking key information about entities
            entity_memory = EntityMemory(
                storage=RAGStorage(
                    embedder_config={
                        "provider": "openai",
                        "config": {
                            "model": 'text-embedding-3-small'
                        }
                    },
                    type="short_term",
                    path="./memory/"
                )
            )
        ) 
