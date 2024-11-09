from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from byaldi import RAGMultiModalModel
from pdf2image import convert_from_path
import base64
import io
from openai import OpenAI

# Initialize your model
RAG = RAGMultiModalModel.from_index("/Users/spartan/Desktop/CMPE 273/hackathon")

# Define FastAPI application
app = FastAPI()

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model for validation
class QueryRequest(BaseModel):
    Query: str

# Function to generate response
def generate_response(query: str):
    results = RAG.search(query, k=3)    
    images = convert_from_path("/Users/spartan/Desktop/CMPE 273/SOFI-2024-1-50-1-10.pdf")
    image_index = results[0]["page_num"] - 1
    buffered = io.BytesIO()
    images[image_index].save(buffered, format="jpeg")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    img_str = f"data:image/jpeg;base64,{img_str}"
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
    )
    
    completion = client.chat.completions.create(
        model="qwen/qwen-2-vl-7b-instruct",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": query},
                {"type": "image_url", "image_url": {"url": img_str}}
            ]
        }]
    )
    return completion.choices[0].message.content

# Root endpoint
@app.get("/")
async def home():
    return {"message": "Welcome to My FastAPI App! Send a POST request to /query with JSON body."}

# Query endpoint
@app.post("/query")
async def handle_query(request: QueryRequest):
    query = request.Query
    if not query:
        raise HTTPException(status_code=400, detail="Query key is missing")

    answer = generate_response(query)
    return {"answer": answer}

# Run the app with: uvicorn filename:app --reload
