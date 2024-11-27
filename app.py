from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_cors import cross_origin

from byaldi import RAGMultiModalModel
from pdf2image import convert_from_path
import base64
import io
from openai import OpenAI
import redis
import requests
import requests
import json
import os

r = redis.Redis(host='localhost', port=6379, db=0)
RAG = RAGMultiModalModel.from_index("/Users/spartan/Desktop/RAG-based-Page-level-Embedding-with-Colpali/content/index")
images = convert_from_path("/Users/spartan/Downloads/2023-nsumhss-annual-report.pdf")

os.environ['OPENAI_API_KEY']=""
chat_history = []
def generate_response(query):
    results = RAG.search(query, k=3)    
    print(results)
    image_index = results[0]["page_num"] - 1
    print(image_index)
    buffered = io.BytesIO()
    images[image_index].save(buffered, format="jpeg")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    img_str = f"data:image/jpeg;base64,{img_str}"
    image_index_2 = results[1]["page_num"] - 1
    print(image_index)
    buffered = io.BytesIO()
    images[image_index_2].save(buffered, format="jpeg")
    img_str_2 = base64.b64encode(buffered.getvalue()).decode()
    img_str_2 = f"data:image/jpeg;base64,{img_str_2}"
    image_index_3 = results[2]["page_num"] - 1
    print(image_index)
    buffered = io.BytesIO()
    images[image_index_3].save(buffered, format="jpeg")
    img_str_3 = base64.b64encode(buffered.getvalue()).decode()
    img_str_3 = f"data:image/jpeg;base64,{img_str_3}"
    
    

    client = OpenAI()

    global chat_history

  # Add user input to chat history
    chat_history.append({"role": "user", "content": query})

    # Prepare messages for the API call
    messages = [{"role": "system", "content": "You are a helpful assistant."}] + chat_history

    # If image_url is provided, add it to the messages
    if img_str:
        messages[-1]["content"] = [
            {"type": "text", "text": query},
            {"type": "image_url", "image_url": {"url": img_str}},
            {"type": "image_url", "image_url": {"url": img_str_2}},
            {"type": "image_url", "image_url": {"url": img_str_3}}


        ]

    # Query the model
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # Add model response to chat history
    chat_history.append({"role": "assistant", "content": completion.choices[0].message.content})

    return completion.choices[0].message.content


app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return 'Welcome to My Flask App! Send a POST request to /query with JSON body.'

@app.route('/query', methods=['POST'])
def handle_query():
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    query = data.get('Query')
    if not query:
        return jsonify({"error": "Query key is missing"}), 400
    
    if r.get(query):
        value = r.get(query)
        
        # Decode the value from bytes to a string
        value = value.decode('utf-8')

        # Set the value again with a 120 seconds expiration
        r.setex(query, time=120, value=value)

        return jsonify({"answer": value}), 200

    answer = generate_response(query)
    r.set(query,answer)
    r.setex(query,time=120,value=answer)

    response = jsonify({"answer": answer})

    return response, 200

if __name__ == "__main__":
    app.run(port=8000)