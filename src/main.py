import langchain
from agents.cyber_agent.run_agent import extecute

print(langchain.__version__)


test_input = "Revisa mi ultimo correo y dime si es phishing"
result= extecute(test_input)
print(result.get("output"))
