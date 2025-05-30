import os
from typing import Dict, List

from langchain_core.tools import tool
from langchain_google_community.gmail.create_draft import GmailCreateDraft
from langchain_google_community.gmail.get_message import GmailGetMessage
from langchain_google_community.gmail.search import GmailSearch
from langchain_google_community.gmail.send_message import GmailSendMessage

from tools.google_toolbox.auth_gmail import AuthGmailToolKit
from tools.google_toolbox.utils import decode_base64

# Obtener las herramientas de Gmail
# El toolkit de Gmail proporciona varias herramientas que puedes utilizar:
# Las herramientas disponibles son:

# GmailCreateDraft: Crear borradores de correo
# GmailSendMessage: Enviar mensajes de correo
# GmailSearch: Buscar correos
# GmailGetMessage: Obtener un mensaje específico
# GmailGetThread: Obtener un hilo de conversación

# toolkit = GmailToolkit()

# # Puedes revisar los alcances en https://developers.google.com/gmail/api/auth/scopes
# credentials = get_gmail_credentials(
#     token_file="token.json",
#     scopes=["https://mail.google.com/"],
#     client_secrets_file="credentials.json",
# )
# api_resource = build_resource_service(credentials=credentials)
# toolkit = GmailToolkit(api_resource=api_resource)


gmail_tool_kit = AuthGmailToolKit()


@tool
def send_draft(message: str, to: List[str], subject: str) -> bool:
    """Enviar borrador de correo electrónico."""

    toolkit = GmailCreateDraft(api_resource=gmail_tool_kit.api_resource)
    result = toolkit.invoke({"message": f"<b>{message}</b>", "to": to, "subject": subject})

    if "Draft created" in result:  # result:  Draft created. Draft Id: r-289637590387318056
        key = result.split()[3]
        value = result.split()[4]

        return {"status": True, key: value}

    return {"status": False, "detail": result}


@tool
def send_message(message: str, to: List[str], subject: str) -> Dict:
    """Enviar correo electrónico."""

    toolkit = GmailSendMessage(api_resource=gmail_tool_kit.api_resource)
    result: str = toolkit.invoke({"message": f"<b>{message}</b>", "to": to, "subject": subject})

    if "Message sent" in result:  # result: Message sent. Message Id: 196d22b086c0e10f
        key = result.split()[3]
        value = result.split()[4]

        return {"status": True, key: value}

    return {"status": False, "detail": result}


@tool
def search_message(query: str = "in:inbox", max_results: int = 3) -> str:
    """
    Busca correos usando operadores de Gmail.
    Soporta: from, to, subject, after, before, has:attachment, etc.
    """
    toolkit = GmailSearch(api_resource=gmail_tool_kit.api_resource)
    result = toolkit.invoke(
        {
            "query": query,
            "max_results": max_results,
        }
    )

    if not result:
        return "No se encontraron correos con esa búsqueda."

    output = []
    for mail in result:
        output.append(f"""ID: {mail.get("id")}
        Remitente: {mail.get("sender")}
        Asunto: {mail.get("subject")}
        Vista previa: {mail.get("snippet")}
        threadId: {mail.get("threadId")}
        Fecha: {mail.get("internalDate", "[sin fecha]")}
        """)

    return "\n---\n".join(output)


@tool
def gmail_get_message(message_id: str) -> str:
    """
    Obtiene y describe un mensaje de Gmail dado su ID.
    Incluye remitente, asunto, fecha, cuerpo de texto y lista de adjuntos.
    """
    toolkit = GmailGetMessage(api_resource=gmail_tool_kit.api_resource)
    message = toolkit.invoke(message_id)

    sender = message.get("from", "No disponible")
    to = message.get("to", "No disponible")
    subject = message.get("subject", "No disponible")
    date = message.get("date", "No disponible")
    body = message.get("text", "No hay contenido de texto disponible")
    attachments = message.get("attachments", [])

    summary = f"""📩 Detalles del correo:
                De: {sender}
                Para: {to}
                Asunto: {subject}
                Fecha: {date}

                📝 Contenido:
                {body}
            """

    if attachments:
        summary += "\n📎 Adjuntos:\n"
        for a in attachments:
            summary += f"- {a['filename']} ({a['mime_type']}, {a['size']} bytes)\n"
    else:
        summary += "\n📎 No se encontraron adjuntos.\n"

    return summary


@tool
def download_from_query(query: str = "from:platzi", max_results: int = 3, gmail_tool_kit=gmail_tool_kit) -> str:
    """
    Busca múltiples correos con una query y descarga cada uno como HTML.
    """

    service = gmail_tool_kit.api_resource

    os.makedirs("correos_html", exist_ok=True)

    results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    messages = results.get("messages", [])

    saved_files = []
    for msg in messages:
        msg_id = msg["id"]
        try:
            message = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
        except Exception:
            continue

        parts = message.get("payload", {}).get("parts", [])
        html = None
        for part in parts:
            if part.get("mimeType") == "text/html":
                html = decode_base64(part["body"]["data"])
                break
        if not html:
            for part in parts:
                if part.get("mimeType") == "text/plain":
                    html = f"<pre>{decode_base64(part['body']['data'])}</pre>"
                    break

        if html:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")
            path = f"correos_html/{msg_id}.html"
            with open(path, "w", encoding="utf-8") as f:
                f.write(soup.prettify())
            saved_files.append(path)

    if not saved_files:
        return "No se encontró contenido descargable."

    return "Correos guardados:\n" + "\n".join(saved_files)
