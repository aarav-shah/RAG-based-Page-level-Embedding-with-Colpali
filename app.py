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
RAG = RAGMultiModalModel.from_index("/Users/spartan/Desktop/CMPE 273/hackathon_final")
images = convert_from_path("/Users/spartan/Desktop/CMPE 273/SOFI-Merged.pdf")
os.environ['OPENAI_API_KEY']="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"

def generate_response(query):
    results = RAG.search(query, k=3)    
    print(results)
    image_index = results[0]["page_num"] - 1
    print(image_index)
    buffered = io.BytesIO()
    images[image_index].save(buffered, format="jpeg")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    img_str = f"data:image/jpeg;base64,{img_str}"
    
    

    client = OpenAI()

    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
        "role": "user",
        "content": [
            {"type": "text", "text": "If statistical analysis is asked in the query, take appropriate approximations from the graphs in the images. Query: "+query},
            {
            "type": "image_url",
            "image_url": {
                "url": img_str
            },
            },
        ],
        }
    ],
    max_tokens=500,
    )
    book_no = "SOFI-2023"
    if image_index+1 > 316:
        image_index-=316
        book_no = "SOFI-2024"
        
    return f"{response.choices[0].message.content }\n##### Source: Pg. No. {image_index+1} of {book_no}"


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