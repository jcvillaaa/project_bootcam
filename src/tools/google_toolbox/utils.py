from langchain_core.messages import BaseMessage
import base64


def decode_base64(data):
    decoded = base64.urlsafe_b64decode(data)
    try:
        return decoded.decode("utf-8")
    except UnicodeDecodeError:
        return decoded.decode("latin1")


def print_pretty_response(response: dict):
    from pprint import pprint

    print("===============================================")
    print("\n🧾 Resumen del flujo de mensajes:\n")
    for msg in response.get("messages", []):
        if isinstance(msg, BaseMessage):
            print(f"\n🔹 Tipo: {type(msg).__name__}")
            print(f"📜 Contenido:\n{msg.content}")
        elif isinstance(msg, dict):
            pprint(msg)
        else:
            print("\n🛑 Mensaje desconocido:\n")
            pprint(msg)