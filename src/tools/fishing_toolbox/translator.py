from langchain_core.tools import tool
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

tokenizer  = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-es-en")
model  = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-es-en")

@tool
def tralate_es_to_en(text: str) -> str:
    """Traduce texto del idioma español al ingles"""
    input= tokenizer(text, return_tensors="pt", padding=True)
    output= model.generate(**input)
    result = tokenizer.batch_decode(output, skip_special_tokens=True)
    return result


if __name__ == "__main__":

    text= "Hola Mundo"

    result= tralate_es_to_en(text)
    print(result)

    traslator = pipeline("translation_es_to_en", model="Helsinki-NLP/opus-mt-es-en")
    print(traslator(text))
