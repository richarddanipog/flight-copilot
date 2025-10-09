from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from src.config import Settings
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from src.utils.logger import get_logger

log = get_logger()
settings = Settings()

llm_instance = None


def get_llm_model():
    global llm_instance

    if llm_instance is not None:
        return llm_instance

    if not settings.groq_api_key:
        llm_instance = ChatOllama(model=settings.model_name)
    else:
        llm_instance = ChatGroq(model='qwen/qwen3-32b', temperature=0.4,
                                api_key=settings.groq_api_key)

    log.info(f"[Using] ModelChat: {llm_instance.__class__.__name__}")
    return llm_instance


def get_chat_prompt_template():
    return ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a helpful travel assistant.\n\n"
            "When the user asks about flights, CALL the `search_flights` tool with complete arguments:\n"
            "- origin (IATA)\n"
            "- destination (IATA)\n"
            "- date_from (YYYY-MM-DD)\n"
            "- return_date (YYYY-MM-DD) when trip length is implied\n"
            "- max_price (number) when budget is implied\n\n"

            "DATE RULES\n"
            "1) Never choose past dates.\n"
            "2) If user gives only a month (e.g., 'in April'), choose the next occurrence IN THE FUTURE of that month "
            "(if the month has passed this year, use next year). Default day = 15th unless range implied.\n"
            "3) If user gives a day without a year, use the current year; if that day already passed, roll to next year.\n"
            "4) If user says 'mid-<month>', use the 15th; 'early'=7th; 'late'=25th; 'end of'=28th.\n"
            "5) If user states duration (e.g., '4–6 days', 'about 5 days', 'a week'), set return_date = date_from + duration:\n"
            "   - ranges: pick the midpoint (e.g., 4–6 → 5 days)\n"
            "   - 'weekend': Friday to Sunday (2 nights)\n"
            "   - 'a week': 7 days\n"
            "6) If user gives a departure window ('mid-November') AND a duration, choose a start date in that window and compute return_date.\n"
            "7) Always format dates as ISO YYYY-MM-DD.\n\n"

            "AIRPORT / CODES\n"
            "- Convert city names to primary IATA (Tel Aviv → TLV, Prague → PRG). "
            "If ambiguous (e.g., 'New York'), pick the main one (JFK) unless user specified otherwise.\n\n"

            "BUDGET\n"
            "- If budget is mentioned, pass max_price and currency.\n\n"

            "CLARITY\n"
            "- Ask at most ONE short follow-up only if a critical field is missing or ambiguous.\n"
            "- If duration is given, DO NOT ask for a return date — compute it.\n\n"

            "OUTPUT\n"
            "- Prefer calling the tool directly rather than explaining reasoning."
        ),

        # FEW-SHOTS (escape curly braces by doubling)
        (
            "human",
            "find me a flight from tel aviv to prague in mid-november, under 500 usd, 4–6 days"
        ),
        (
            "ai",
            "(calls search_flights with) {{\"origin\": \"TLV\", \"destination\": \"PRG\", "
            "\"date_from\": \"2025-11-15\", \"return_date\": \"2025-11-20\", \"max_price\": 500}}"
        ),
        (
            "human",
            "tlv to bcn early december for a week non stop"
        ),
        (
            "ai",
            "(calls search_flights with) {{\"origin\": \"TLV\", \"destination\": \"BCN\", "
            "\"date_from\": \"2025-12-07\", \"return_date\": \"2025-12-14\", \"nonstop\": true}}"
        ),
        (
            "human",
            "flight to rome on 10/10 for 5 days"
        ),
        (
            "ai",
            "(calls search_flights with) {{\"origin\": \"TLV\", \"destination\": \"FCO\", "
            "\"date_from\": \"2025-10-10\", \"return_date\": \"2025-10-15\"}}"
        ),
        (
            "human",
            "new york next month weekend"
        ),
        (
            "ai",
            "(calls search_flights with) {{\"origin\": \"TLV\", \"destination\": \"JFK\", "
            "\"date_from\": \"<next month Fri>\", \"return_date\": \"<next month Sun>\"}}"
        ),

        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])
