from langchain_core.tools import tool
from torch import argmax
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

tokenizer_phishing = AutoTokenizer.from_pretrained("ealvaradob/bert-finetuned-phishing")
model_ealvaradob = AutoModelForSequenceClassification.from_pretrained("ealvaradob/bert-finetuned-phishing")

model_elslay = pipeline("text-classification", model="ElSlay/BERT-Phishing-Email-Model")


@tool
def phishing_ealvaradob(text: str):
    """Clasificador de phishing, recibe emails(html/text), urls, text, sms"""
    input = tokenizer_phishing(text, return_tensors="pt", padding=True)
    output = model_ealvaradob(**input)
    logits = output.logits
    probabilidades = logits.softmax(dim=1)
    prediccion_id = argmax(probabilidades, dim=1)
    lista_resultados = []

    for i in range(len(prediccion_id)):
        pred_id = prediccion_id[i].item()
        etiqueta_predicha = model_ealvaradob.config.id2label[pred_id]
        prob_predicha = probabilidades[i, pred_id].item()

        resultado = {
            "prediccion": "phishing" if etiqueta_predicha == "phishing" else "benigno",
            "probabilidad": prob_predicha,
        }
        lista_resultados.append(resultado)
    return lista_resultados


@tool
def phishing_elslay(text: str):
    """Clasificador de phishing, recibe emails(html/text), urls, text, sms"""
    resultado = model_elslay(text)
    lista_resultados = []
    for i in range(len(resultado)):
        pred_id = resultado[i]["label"]
        prob_predicha = resultado[i]["score"]

        resultado = {"prediccion": "phishing" if pred_id == "LABEL_1" else "benigno", "probabilidad": prob_predicha}
        lista_resultados.append(resultado)
    return lista_resultados



if __name__ == "__main__":
    text = """
        PRESI03-1-Inteligencia artificial Innovador - Avanzado-2025-1-L1-ANTIOQUIA-G47 (UNIMINUTO) cambio de contenido
    """

    result = phishing_ealvaradob(text)
    print(result)

    result = phishing_elslay(text)
    print(result)



