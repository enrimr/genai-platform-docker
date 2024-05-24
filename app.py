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

# Cargar configuración desde config.json
with open('config.json') as f:
    config = json.load(f)

# Cargar configuración de modelos desde models_config.json
with open('models_config.json') as f:
    models_config = json.load(f)

# Verificar si el modelo es sample-based
is_sample_based = models_config.get(model_name, {}).get('sample_based', True)

# Cargar el modelo y el tokenizador con el token de autenticación
model = AutoModelForCausalLM.from_pretrained(model_name, token=hf_token)
tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)

@app.route('/')
def home():
    return render_template('index.html', config=config, is_sample_based=is_sample_based, model_name=model_name)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    prompt = data.get('prompt', '')
    max_new_tokens = data.get('max_new_tokens', config['max_new_tokens'])
    temperature = data.get('temperature', config['temperature']) if is_sample_based else None
    top_k = data.get('top_k', config['top_k']) if is_sample_based else None
    top_p = data.get('top_p', config['top_p']) if is_sample_based else None
    fields = data.get('fields', [])
    do_sample = is_sample_based

    inputs = tokenizer(prompt, return_tensors="pt")
    input_ids = inputs['input_ids']
    attention_mask = inputs['attention_mask']
    
    start_time = time.time()  # Iniciar el cronómetro
    
    # Generar el texto con los parámetros especificados
    generation_args = {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "max_new_tokens": max_new_tokens,
        "do_sample": do_sample,
        "pad_token_id": tokenizer.eos_token_id
    }
    
    if is_sample_based:
        generation_args.update({
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p
        })
    
    outputs = model.generate(**generation_args)
    
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
