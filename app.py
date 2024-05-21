from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import torch

app = Flask(__name__)

# Obtener el nombre del modelo y el token desde las variables de entorno
model_name = os.getenv('MODEL_NAME', 'gpt2')
hf_token = os.getenv('HF_TOKEN')

# Cargar el modelo y el tokenizador con el token de autenticación
model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=hf_token, torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=hf_token)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    prompt = data.get('prompt', '')
    max_length = data.get('max_length', 100)
    temperature = data.get('temperature', 1.0)
    top_k = data.get('top_k', 50)
    top_p = data.get('top_p', 1.0)
    
    inputs = tokenizer(prompt, return_tensors="pt")
    input_ids = inputs['input_ids']
    attention_mask = inputs['attention_mask']
    
    # Generar el texto con los parámetros especificados
    outputs = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_length=max_length,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        pad_token_id=tokenizer.eos_token_id
    )
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return jsonify({"generated_text": generated_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
