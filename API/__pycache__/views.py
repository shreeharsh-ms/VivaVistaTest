
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import json
import PyPDF2
import google.generativeai as genai
import csv
import pymongo
from datetime import datetime

# Configure the Gemini API key
genai.configure(api_key="AIzaSyCEI1mwJSop93eUAvqURlGmo1bgvmR1KUA")

# Set up the model configuration
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 55,
    "max_output_tokens": 9000,
    "response_mime_type": "application/json",
}

# Initialize the Gemini model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

# Function to generate questions using Gemini AI
def generate_questions_gemini(pdf_text, num_understanding=20, num_remembering=15, num_mcqs=5, num_application=10):
    system_prompt = f"""
    Document: {pdf_text}
    Based on the provided document, generate questions in the following categories. Ensure the questions are detailed and relevant, covering key concepts from across the document.
    Structure the output in JSON format, where each question will have a category and a text field.
    Example structure for each question:
    {{
      "Understanding questions": [
        "What are the key factors that contributed to Sachin Tendulkar's early success in cricket?",
        # ... (Other questions)
      ],
      "Remembering level questions": [
        "When and where was Sachin Tendulkar born?",
        # ... (Other questions)
      ],
      "Application level questions": [
        "If you were to write a motivational speech for aspiring cricketers, how would you use Sachin Tendulkar's life as an example?",
        # ... (Other questions)
      ],
      "Multiple-choice questions": [
        {{
          "question": "What is Sachin Tendulkar's nickname?",
          "options": [
            "The Master Blaster",
            "The Little Master",
            "The God of Cricket",
            "All of the above"
          ]
        }},
        # ... (Other MCQs)
      ]
    }}

    1. **Understanding Questions**: 
    - These questions should focus on the key concepts, relationships, and ideas presented in the document.
    - Generate {num_understanding} such questions.

    2. **Remembering Level Questions**: 
    - Fact-based questions focusing on recalling specific information from the document.
    - Generate {num_remembering} such questions.

    3. **Application Level Questions**: 
    - Apply the concepts from the document to real-world scenarios or practical situations.
    - Generate {num_application} such questions.

    4. **Multiple-Choice Questions (MCQs)**: 
    - Each question should have 4 options. Generate {num_mcqs} MCQs.

    Generate not less not more questions than specified numbers.
    """
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(system_prompt)
    try:
        return json.loads(response.text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

# Function to store JSON data in MongoDB
def store_json_in_mongodb(json_data, subject_name, collection_name="Question_Generated", db_name="Viva_Viva_Online_db"):
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client[db_name]
        collection = db[collection_name]
        document = {
            "subject_name": subject_name,
            "Created_at": datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            "data": json_data
        }
        collection.insert_one(document)
        print(f"Data successfully written to MongoDB.")
    except pymongo.errors.ConnectionError as e:
        print(f"Could not connect to MongoDB: {e}")

# Function to convert JSON to CSV
def write_json_to_csv(json_data, csv_filename):
    try:
        os.makedirs(os.path.dirname(csv_filename), exist_ok=True)
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Category', 'Question', 'Options'])
            for category, questions in json_data.items():
                if isinstance(questions, list):
                    if isinstance(questions[0], str):
                        for question in questions:
                            writer.writerow([category, question, None])
                    elif isinstance(questions[0], dict):
                        for mcq in questions:
                            question = mcq.get('question', '')
                            options = ' | '.join(mcq.get('options', []))
                            writer.writerow([category, question, options])
        print(f"Data successfully written to CSV file: {csv_filename}")
    except Exception as e:
        print(f"Error writing to CSV: {e}")

# Main function

def main(pdf_path, subject_name):
    pdf_text = extract_text_from_pdf(pdf_path)
    if pdf_text:
        questions = generate_questions_gemini(pdf_text)
        if questions:
            csv_file_path = f'VivaVista_with_AI_Proctor/Generated_Questions/{subject_name}.csv'
            write_json_to_csv(questions, csv_file_path)
            store_json_in_mongodb(questions, subject_name)
    else:
        print("No text extracted from PDF.")
SubjectName = 'Subject1'
# Upload PDF View

def upload_pdf(request):
    if request.method == 'POST' and request.FILES['pdfFile']:
        uploaded_file = request.FILES['pdfFile']
        print(upload_pdf)
        save_directory = os.path.join(settings.MEDIA_ROOT, 'DataRepo', 'ram', 'Material')
        print("Fileeeee: ",save_directory)
        os.makedirs(save_directory, exist_ok=True)
        fs = FileSystemStorage(location=save_directory)
        print(fs)
        filename = fs.save(uploaded_file.name, uploaded_file)
        print(filename)
        uploaded_file_url = fs.url(filename)
        print("uploaded file : ", uploaded_file_url)
        NewFileName = f"{save_directory}\{filename}"
        main(NewFileName,SubjectName)
        # return render(request, 'upload_success.html', {'uploaded_file_url': uploaded_file_url})
    return render(request, 'index.html')

# Schedule Viva View
def schedule_viva(request):
    if request.method == 'POST':
        viva_data = {
            "viva_date": request.POST.get('vivaDate'),
            "viva_time": request.POST.get('vivaTime'),
            "subject_name": request.POST.get('subjectName'),
            "num_questions": request.POST.get('numQuestions'),
            "question_source": request.POST.get('questionSource'),
            "generate_option": request.POST.get('generateOption'),
        }
        print("Viva scheduled:", viva_data)
        return HttpResponse("Viva scheduled successfully!")
    return render(request, 'schedule_viva.html')

# In views.py
from django.http import JsonResponse
from pymongo import MongoClient
from django.conf import settings

def get_questions(request):
    client = MongoClient(settings.MONGO_URI)  # Add your MongoDB URI in settings
    db = client['Viva_Viva_Online_db']  # replace with your DB name
    collection = db['Question_Generated']  # replace with your collection name
    question_data = collection.find_one({"subject_name": SubjectName})  # Use appropriate query
    
    if question_data:
        # Structure response
        response_data = {
            "understanding_questions": question_data["data"]["Understanding questions"],
            "remembering_level_questions": question_data["data"]["Remembering Level Questions"],
            "application_level_questions": question_data["data"]["Application Level Questions"],
            "multiple_choice_questions": question_data["data"]["Multiple-choice questions"]
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({"error": "Data not found"}, status=404)

# Static page views
def home(request):
    return render(request, 'index.html')

def STDlogin(request):
    return render(request, 'STDlogin.html')

def STDconf(request):
    return render(request, 'STDconf.html')

def STDpass(request):
    return render(request, 'STDpass.html')

def STDashboard(request):
    return render(request, 'STDashboard.html')
