from flask import Flask, request, jsonify, render_template
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import torch
import time
import json

app = Flask(__name__, static_url_path='/static')

# Obtener el nombre del modelo y el token desde las variables de entorno
model_name = os.getenv('MODEL_NAME', 'openai-community/gpt2')
hf_token = os.getenv('HF_TOKEN')

# Cargar el modelo y el tokenizador con el token de autenticación
model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=hf_token)
tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=hf_token)

# Cargar configuración desde config.json
with open('config.json') as f:
    config = json.load(f)

@app.route('/')
def home():
    return render_template('index.html', config=config)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    prompt = data.get('prompt', '')
    max_new_tokens = data.get('max_new_tokens', config['max_new_tokens'])
    temperature = data.get('temperature', config['temperature'])
    top_k = data.get('top_k', config['top_k'])
    top_p = data.get('top_p', config['top_p'])
    fields = data.get('fields', [])

    inputs = tokenizer(prompt, return_tensors="pt")
    input_ids = inputs['input_ids']
    attention_mask = inputs['attention_mask']
    
    start_time = time.time()  # Iniciar el cronómetro
    
    # Generar el texto con los parámetros especificados
    outputs = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        pad_token_id=tokenizer.eos_token_id
    )
    
    end_time = time.time()  # Detener el cronómetro
    latency = end_time - start_time  # Calcular la latencia

    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Elimina el texto del prompt de la respuesta generada
    if generated_text.startswith(prompt):
        generated_text = generated_text[len(prompt):].strip()
    
    response = {}
    if 'generated_text' in fields:
        response['generated_text'] = generated_text
    if 'input_token_count' in fields:
        response['input_token_count'] = len(input_ids[0])
    if 'output_token_count' in fields:
        response['output_token_count'] = len(outputs[0])
    if 'latency' in fields:
        response['latency'] = latency

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
