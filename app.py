from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import torch

app = Flask(__name__)

# Obtener el nombre del modelo desde una variable de entorno
model_name = os.getenv('MODEL_NAME', 'gpt2')

# Cargar el modelo y el tokenizador
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained(model_name)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    prompt = data.get('prompt', '')
    max_length = data.get('max_length', 100)
    temperature = data.get('temperature', 1.0)
    top_k = data.get('top_k', 50)
    top_p = data.get('top_p', 1.0)
    
    inputs = tokenizer(prompt, return_tensors="pt")
    
    # Generar el texto con los parámetros especificados
    outputs = model.generate(
        inputs['input_ids'],
        max_length=max_length,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p
    )
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return jsonify({"generated_text": generated_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
