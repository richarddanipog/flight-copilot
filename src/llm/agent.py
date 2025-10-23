import json
from typing import List, Dict, Any, Tuple
from src.config import Settings
from langchain.agents import AgentExecutor, create_tool_calling_agent
from src.llm.tools.flight_tool import search_flights_tool
from src.utils.logger import get_logger
from src.utils.llm import get_chat_prompt_template, get_llm_model
from src.utils.date_guard import validate_dates_in_query, PastDateError
from langchain.memory import ConversationBufferWindowMemory

settings = Settings()


class LLMAgent:
    def __init__(self):
        self.llm = get_llm_model()
        self.log = get_logger()
        self.executor = None

    def init_executor(self):
        if self.executor is not None:
            return self.executor

        tools = [search_flights_tool()]
        prompt = get_chat_prompt_template()

        agent = create_tool_calling_agent(
            llm=self.llm, tools=tools, prompt=prompt)

        memory = ConversationBufferWindowMemory(
            memory_key='chat_history', return_messages=True, input_key='input', output_key='output'
        )

        self.executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=settings.use_verbose,
            return_intermediate_steps=True,
        )

        return self.executor

    def execute(self, **kwargs) -> Tuple[List[Dict[str, Any]], str]:
        agent_query = kwargs.get("agent")

        try:
            validate_dates_in_query(agent_query)
        except PastDateError as e:
            raise ValueError(f"[ERROR] {e}")

        executor = self.init_executor()

        try:
            result = executor.invoke({"input": agent_query})
        except Exception as e:
            self.log.error("Agent failed: %s", e)
            raise Exception("Agent failed: %s", e)

        steps = result.get("intermediate_steps", [])
        itineraries = []
        tool_args = {}
        if steps:
            action, observation = steps[-1]
            if isinstance(observation, str):
                try:
                    itineraries = json.loads(observation)
                except Exception:
                    itineraries = None
            elif isinstance(observation, list):
                itineraries = observation

            tool_args = getattr(action, "tool_input", {}) or {}

        if itineraries == [] and tool_args.get("return_date") and tool_args.get("nonstop"):
            relaxed = {**tool_args, "nonstop": False}
            itineraries = search_flights_tool().invoke(relaxed)

        return itineraries, result.get("output", "")
