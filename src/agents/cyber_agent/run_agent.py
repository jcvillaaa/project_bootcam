from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from tools.fishing_toolbox.translator import tralate_es_to_en
from tools.fishing_toolbox.base import phishing_ealvaradob
from tools.google_toolbox.tools_gmail import download_from_query, gmail_get_message, search_message, send_draft, send_message
from tools.google_toolbox.utils import print_pretty_response

# Herramientas comunes
tools = [send_draft, send_message, search_message, gmail_get_message, download_from_query, phishing_ealvaradob, tralate_es_to_en]

# LLM común
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-001")


promt= """
            Eres un asistente experto en detectar phishing en correos electrónicos (Emails).
            Siempre que te pregunten por correos primero busca los ids de los correos que te preguntan
            Siempre que te falte informacion de algun correo usa alguna de las herramientas para completarla
            Siempre que te pregunten por correos, usa las herramientas disponible.
            Responde con el remitente, asunto y resumen del contenido.
            Sempre junta herramientas si es necesario para encontrar una posible solucion.
            Si necesitas operar sobre algun emil siemmpre busca su id primero
            Nunca digas que no sabes si la herramienta está disponible.
        """


def run_react_agent(input_text: str):
    agent = create_react_agent(llm, tools)
    # Prompt base para ReAct Agent (flexible)
    system_msg = SystemMessage(content=(promt))
    user_message = HumanMessage(content=input_text)

    response = agent.invoke({"messages": [system_msg, user_message]})
    return response


def run_tool_calling_agent(input_text: str):
    # Prompt con agent_scratchpad obligatorio para Tool Calling Agent
    prompt = ChatPromptTemplate.from_messages([("system", promt), ("user", "{input}"), MessagesPlaceholder(variable_name="agent_scratchpad")])
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    response = executor.invoke({"input": input_text})
    return response


def extecute(test_input: str):
    # print("==== ReAct Agent ====")
    # resp_react = run_react_agent(test_input)
    # print_pretty_response(resp_react)

    print("\n==== Tool Calling Agent ====")
    resp_tool_call = run_tool_calling_agent(test_input)
    # print(resp_tool_call)
    # print_pretty_response(resp_tool_call)

    return resp_tool_call

if __name__ == "__main__":
    test_input = "Revisa mi tercer correo y dime si es phishing"
    extecute(test_input)
