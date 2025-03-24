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
from django.http import JsonResponse
import csv
import random
# Configure the Gemini API key
genai.configure(api_key="AIzaSyBlT5Ix1izu7l4El1zoj1Xm64aIAYo9L9o")

# Set up the model configuration
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 40,
    "max_output_tokens": 8192,
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
def generate_questions_gemini(pdf_text, num_understanding=10, num_remembering=20, num_mcqs=10, num_application=10):
    system_prompt = f"""
    Document: {pdf_text}
    Based on the provided document, generate simple and easy-to-answer questions that can be easily understood and answered during a real-time online conversation. Focus on asking straightforward questions that assess basic understanding and can be answered concisely. Ensure that each question is relevant to the key concepts from the document.
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
    print(json.loads(response.text))
    try:
        return json.loads(response.text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

# Function to store JSON data in MongoDB
import uuid
from django.http import JsonResponse
def store_json_in_mongodb(request, json_data, collection_name="Question_Generated", db_name="Viva_Viva_Online_db"):
    from datetime import datetime
    try:
        client = pymongo.MongoClient("mongodb+srv://shree:shree%401234@cluster0.fhplq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client[db_name]
        collection = db[collection_name]
        classroom_code = request.session.get('classroom_code')
        # subject_name = request.session.get('subjectName')
        
        # Generate a unique ID
        unique_id = str(uuid.uuid4())  # Generates a unique identifier
        request.session['question_id'] = unique_id
        subject_name = "Test_subject"
        
        document = {
            "_id": unique_id,  # MongoDB's default field for unique identification
            "classroom_code": classroom_code,
            "subject_name": subject_name,
            "timestamp": datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            "data": json_data
        }
        
        collection.insert_one(document)
        print(f"Data successfully written to MongoDB with ID: {unique_id}")
        return unique_id  # Return the unique ID for future use
    except pymongo.errors.DuplicateKeyError:
        print(f"Duplicate ID error. Record with ID {unique_id} already exists.")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred: {e}")



import pymongo

def fetch_questions_from_mongodb(request, collection_name="Question_Generated", db_name="Viva_Viva_Online_db"):
    """
    Fetches all questions from the latest record in a MongoDB collection.

    Parameters:
        collection_name (str): The name of the MongoDB collection to query.
        db_name (str): The name of the MongoDB database.

    Returns:
        list: A list of all questions from the latest record in the collection.
              Returns an empty list if no record is found or an error occurs.
    """
    print("*****************Fetch Func Called*****************88")
    try:
        # Establish MongoDB connection
        client = pymongo.MongoClient("mongodb+srv://shree:shree%401234@cluster0.fhplq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client[db_name]
        collection = db[collection_name]
        classroom_code = request.session.get('ongoing_viva_classroom_code')
        SubjectName = request.session.get('ongoing_viva_subjectname_new')
        print(SubjectName)
        print(classroom_code)
        
        # Fetch the latest record (assuming a 'timestamp' field exists)
        
        latest_record = collection.find_one(
    {
        "classroom_code": classroom_code,  # Replace with the specific classroom code
        "subject_name" : SubjectName                             # Replace with the specific subject name
    }
    # sort=[("timestamp", -1)]
)
        if not latest_record:
            print("No sessions available.")
            return []
        
        # Extract the 'data' field
        document = latest_record['data']
        understanding_questions = document.get('Understanding questions', [])
        remembering_questions = document.get('Remembering level questions', [])
        application_questions = document.get('Application level questions', [])
        mcqs = document.get('Multiple-choice questions', [])
        
        # Combine all questions into one list
        all_questions = understanding_questions + remembering_questions + application_questions
        mcq_questions = [mcq.get('question', '') for mcq in mcqs]  # Extract MCQ questions
        all_questions += mcq_questions
        print("From Fetch Function: ")
        print(type(all_questions))
        print(all_questions)
        return all_questions
        



        # Combine all questions into a single list
        # all_questions = []
        # for category in [
        #     'Understanding questions', 
        #     'Remembering level questions', 
        #     'Application level questions', 
        #     'Multiple-choice questions'
        # ]:
        #     category_questions = document.get(category, [])
        #     if category == 'Multiple-choice questions':
        #         # Extract the 'question' field from each MCQ
        #         category_questions = [mcq.get('question', '') for mcq in category_questions]
        #     all_questions.extend(category_questions)
        
        # return all_questions
    
    except pymongo.errors as e:
        print(f"Database connection error: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        # Close the MongoDB connection
        client.close()

# Function to randomly select questions


def select_random_questions(all_questions, num_questions):
    """
    Select a specified number of unique random questions from a given iterable.

    Parameters:
        all_questions (list|dict|set): A collection of all available questions.
        num_questions (int): The number of questions to select.
    
    Returns:
        list: A list of randomly selected questions. Returns an empty list if:
              - The number of requested questions exceeds the available questions.
              - The input type is unsupported or invalid.
    """
    # Ensure the number of questions is valid
    if num_questions <= 0:
        print("Error: Number of questions must be greater than zero.")
        return []

    # Convert `all_questions` to a list if necessary
    if isinstance(all_questions, dict):
        all_questions = list(all_questions.values())  # Use values by default
    elif isinstance(all_questions, set):
        all_questions = list(all_questions)
    elif not isinstance(all_questions, list):
        print("Error: Unsupported input type. Expected list, dict, or set.")
        return []

    # Ensure enough questions are available
    if len(all_questions) < num_questions:
        print(f"Error: Not enough questions available. Requested {num_questions}, but only {len(all_questions)} provided.")
        return []

    # Select random questions
    selected_questions = random.sample(all_questions, num_questions)
    return selected_questions

def main(request, pdf_path):
    from django.http import JsonResponse
    pdf_text = extract_text_from_pdf(pdf_path)
    
    if pdf_text:
        questions = generate_questions_gemini(pdf_text)
        if questions:
            # csv_file_path = f'VivaVista_with_AI_Proctor/Generated_Questions/{subject_name}.csv'
            # write_json_to_csv(questions, csv_file_path)
            unique_id = store_json_in_mongodb(request, questions)
            return questions, unique_id
    else:
        print("No text extracted from PDF.")


# Upload PDF View

def upload_pdf(request):
    if request.method == 'POST' and 'pdfFile' in request.FILES:
        try:
            uploaded_file = request.FILES['pdfFile']
            save_directory = os.path.join(settings.MEDIA_ROOT, 'DataRepo', 'ram', 'Material')
            os.makedirs(save_directory, exist_ok=True)

            fs = FileSystemStorage(location=save_directory)
            filename = fs.save(uploaded_file.name, uploaded_file)
            NewFileName = os.path.join(save_directory, filename)
            print("File saved as: ", NewFileName)

            questions, _ = main(request, NewFileName)  # Process the file

            # Save the questions to the session
            request.session['questions'] = questions
            request.session.modified = True

            return JsonResponse({"success": True, "questions": questions})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request or no file uploaded"})

# Schedule Viva View
def questions(request):
    questions = request.session.get('questions', {})
    return render(request, 'questions.html', {"questions": questions})

def download_csv(request, user_id=None, subject_name="default_subject"):
    # Retrieve questions from the session
    questions_data = request.session.get('questions', {})
    if not questions_data:
        return HttpResponse("No questions found in the session.", status=404)

    # Define file save path, use "unUserID" if user_id is not provided
    folder_name = str(user_id) if user_id else "unUserID"
    base_dir = os.path.join(settings.BASE_DIR, "VivaVista_with_AI_Proctor", "QuestionBank", folder_name)
    os.makedirs(base_dir, exist_ok=True)  # Create directories if not already existing
    file_path = os.path.join(base_dir, f"{subject_name}.csv")

    # Write questions data to a local CSV file
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Category', 'Type', 'Question', 'Options (if applicable)', 'Answer (if applicable)'])

        for category, questions in questions_data.items():
            for question in questions:
                if isinstance(question, dict):  # For multiple-choice questions
                    writer.writerow([
                        category, 
                        "Multiple-choice", 
                        question.get('question', ''), 
                        "; ".join(question.get('options', [])), 
                        question.get('answer', '')
                    ])
                else:  # For other types of questions
                    writer.writerow([category, "Text-based", question, '', ''])

    # Create a response object for download
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{subject_name}.csv"'

    # Write the same data to the response for download
    with open(file_path, mode='r', encoding='utf-8') as file:
        response.write(file.read())

    return response

from django.views.decorators.http import require_POST

@require_POST
def schedule_viva(request):
    """
    View to schedule a viva by saving details to a MongoDB collection.
    """
    try:
        collection = settings.MONGO_DB['scheduled_viva']
        notifications_collection = settings.MONGO_DB['notifications']
        questions_collection = settings.MONGO_DB['Question_Generated']
        question_id = request.session.get('question_id')

        if request.method == "POST":
            data = json.loads(request.body)

            classroom_code = request.session.get('classroom_code', None)
            print("Classroom code: ", classroom_code)
            # Validate and save data
            required_fields = ['vivaDate', 'vivaTime', 'subjectName', 'numQuestions', 'questionSource']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400)

            if classroom_code:
                data['classroom_code'] = classroom_code

            notifications_collection.insert_one({'notification': (f"Viva scheduled for Subject {data['subjectName']} on date {data['vivaDate']} at {data['vivaTime']}."),
                                                 'classroom_code': data['classroom_code']})

            subjectName = data['subjectName']
            print(subjectName)
            # Perform the update
            result = questions_collection.update_one(
                {"_id": question_id},  # Find the document by _id
                {
                    "$set": {  # Update the specific fields
                        "subject_name": subjectName,
                        "classroom_code": data['classroom_code']
                    }
                }
            )

            # Print the result of the update
            if result.matched_count > 0:
                print(f"Successfully updated {result.modified_count} document(s).")
            else:
                print("No matching document found.")

            # request.session['subjectName']
            # data['classroom_code'] = classroom_code
            print("Scheduled viva data: ", data)
            collection.insert_one(data)
            # collection.update_one({'classroom_code': classroom_code}, {'$set': data}, upsert=True)

            return JsonResponse({
                "message": "Viva details submitted successfully!",
                "redirect_url": "/"  # Replace with the desired success page route
            }, status=200)

        elif request.method == "GET":
            # Redirect or return a response for direct GET access
            return redirect('host_dashboard')  # Redirect to success page or another route

        else:
            return JsonResponse({"error": "Invalid request method"}, status=405)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)  
# In views.py
from django.http import JsonResponse
from pymongo import MongoClient
from django.conf import settings

# def get_questions(request):
#     client = MongoClient(settings.MONGO_URI)  # Add your MongoDB URI in settings
#     db = client['Viva_Viva_Online_db']  # replace with your DB name
#     collection = db['Question_Generated']  # replace with your collection name
#     question_data = collection.find_one({"subject_name": SubjectName})  # Use appropriate query
    
#     if question_data:
#         # Structure response
#         response_data = {
#             "understanding_questions": question_data["data"]["Understanding questions"],
#             "remembering_level_questions": question_data["data"]["Remembering Level Questions"],
#             "application_level_questions": question_data["data"]["Application Level Questions"],
#             "multiple_choice_questions": question_data["data"]["Multiple-choice questions"]
#         }
#         return JsonResponse(response_data)
#     else:
#         return JsonResponse({"error": "Data not found"}, status=404)


# Extraction of input text
from django.http import JsonResponse
import json

# def process_transcript(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)  # Parse the JSON data from the request
#             transcript = data.get('transcript', '')  # Get the transcript text
#             # Do something with the transcript, like saving it or processing it
#             print(f"Received transcript: {transcript}")
            
#             # Respond back to the frontend
#             return transcript
#             return JsonResponse({'message': 'Transcript received successfully', 'transcript': transcript})
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON'}, status=400)
#     return JsonResponse({'error': 'Invalid method'}, status=405)

# def compare_results(query, user_response):

#     model2 = genai.GenerativeModel(
#         model_name="gemini-1.5-flash",
#         system_instruction='''
#         Context:
#         You are an AI evaluator assigned to assess the quality of responses provided by a student during a viva exam. Your role is to evaluate each response based on several criteria and generate an accuracy score between 1 and 10.
#         Only return or give an accuracy score that is between 1 and 10. No other information is needed.
#         '''
#     )
    
#     prompt = f'''
#     Question: {query}
#     User's response: {user_response}
#     '''
    
#     try:
#         # Generate a response
#         response = model2.generate_content(prompt)
#         score = response.text.strip()  # Clean the response
        
#         # Validate and convert score to float
#         score_float = float(score)
#         if 1 <= score_float <= 10:  # Ensure score is within the valid range
#             print(f"Score: {score_float}")
#             return score_float
#         else:
#             raise ValueError(f"Invalid score range: {score}")
    
#     except ValueError as e:
#         print(f"Error processing score: {e}")
#         return None  # Or handle the error differently (e.g., return a default score)
#     except Exception as e:
#         print(f"Unexpected error: {e}")
#         return None


from django.http import JsonResponse
import json
from pymongo import MongoClient


def process_transcript(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request
            data = json.loads(request.body)
            print(data)
            viva_session_id = request.session.get('viva_session_id')
            print("process transcript: ", viva_session_id)

            # Ensure a valid session ID exists
            if not viva_session_id:
                return JsonResponse({'error': 'Viva session ID is missing.'}, status=400)

            question = data.get('question', '').strip()
            transcript = data.get('transcript', '').strip()
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@Viva Session id: ", viva_session_id)
            print("Question from transcript: ", question)
            print("Transcript from transcript: ", transcript)

            if not question:
                return JsonResponse({'error': 'Both question and transcript are required.'}, status=400)
            
            if not transcript:
                transcript = 'null'

            # MongoDB setup
            client = MongoClient("mongodb+srv://shree:shree%401234@cluster0.fhplq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # Replace with your MongoDB URI
            db = client["Viva_Viva_Online_db"]  # Replace with your database name
            transcripts_collection = db["transcripts"]  # Replace with your collection name

            # Store the question and transcript in MongoDB
            transcript_data = {
                "session_id": viva_session_id,
                "question": question,
                "transcript": transcript,
                "evaluation_score": None  # Placeholder for AI evaluation
            }
            transcript_id = transcripts_collection.insert_one(transcript_data).inserted_id
            print(f"Stored question and transcript with ID: {transcript_id}")

            # Save the transcript data to the session
            session_transcripts = request.session.get('transcripts', [])
            session_transcripts.append({
                "question": question,
                "transcript": transcript,
                "evaluation_score": None  # Placeholder for AI evaluation
            })
            request.session['transcripts'] = session_transcripts

            # AI Model setup
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=''' 
                Context:
                You are an AI evaluator assigned to assess the quality of responses provided by a student during a viva exam. Your role is to evaluate each response based on several criteria and generate an accuracy score between 1 and 10.
                Only return or give an accuracy score that is between 1 and 10. No other information is needed.
                '''
            )

            # Generate evaluation score using the AI model
            prompt = f'''
            Question: {question}
            User's response: {transcript}
            '''
            ai_response = model.generate_content(prompt)
            score = float(ai_response.text.strip())

            # Validate score
            if not (1 <= score <= 10):
                raise ValueError("Score out of range.")

            # Update MongoDB with the evaluation score
            transcripts_collection.update_one(
                {"_id": transcript_id},
                {"$set": {"evaluation_score": score}}
            )
            print(f"Evaluation score updated in MongoDB: {score}")
            
            # Update the session transcript with the score
            for transcript in session_transcripts:
                if transcript['question'] == question and transcript['transcript'] == transcript:
                    transcript['evaluation_score'] = score
            request.session['transcripts'] = session_transcripts

            print("Session Transcripts: ", request.session.get('transcripts', []))


            # Return the response
            return JsonResponse({
                'message': 'Transcript processed successfully',
                'session_id': viva_session_id,
                'question': question,
                'transcript': transcript,
                'score': score,
                'session_transcripts': session_transcripts  # Optional: Include all transcripts for debugging
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except ValueError as ve:
            print(f"Value Error: {ve}")
            return JsonResponse({'error': 'Invalid evaluation score generated'}, status=500)
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

    return JsonResponse({'error': 'Invalid method'}, status=405)



# Static page views
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required


# def home(request):
#     from datetime import datetime, date
#     try:
#         # Connect to MongoDB collections
#         classrooms = settings.MONGO_DB['classrooms']
#         schedule_viva_collection = settings.MONGO_DB['scheduled_viva']
#         current_date = datetime.now().date()
#         classroom_code = request.session.get('classroom_code')
#         host_name = request.session.get('username')
#         host_id = request.session.get('host_id')
        
#         # Fetch all scheduled viva data
#         all_scheduled_viva = schedule_viva_collection.find()
#         matching_vivas = schedule_viva_collection.find({'classroom_code': classroom_code})
#         viva_data = [
#     {
#         'id': str(record['_id']),  # Convert ObjectId to string
#         **{key: value for key, value in record.items() if key != '_id'}
#     }
#     for record in matching_vivas
# ]
#         past_vivas = [viva for viva in viva_data if datetime.strptime(viva['vivaDate'], "%Y-%m-%d").date() < current_date ]
#         upcoming_vivas = [viva for viva in viva_data if datetime.strptime(viva['vivaDate'], "%Y-%m-%d").date() >= current_date]

#         # Fetch all classroom data
#         all_classrooms = classrooms.find()
#         classrooms_data = [{'id': str(classroom['_id']), **classroom} for classroom in all_classrooms]
#         print(classrooms_data)

#         print(classroom_code)
#         print(host_id)

#         host_classroom = classrooms.find_one({'classroom_code': classroom_code, 'host_id': host_id})
#         print("Host Classroom: ", host_classroom)
#         # Prepare context for the template
#         context = {
#             'classrooms': host_classroom,
#             'past_vivas': past_vivas,
#             'upcoming_vivas': upcoming_vivas,
#             'host_name': host_name
#         }

#         return render(request, 'index.html', context)

#     except Exception as e:
#         # Log the error and return an HTTP response for debugging
#         return HttpResponse(f"Error: {str(e)}", content_type="text/plain")

def home(request):
    from datetime import datetime, date
    try:
        # Connect to MongoDB collections
        classrooms = settings.MONGO_DB['classrooms']
        schedule_viva_collection = settings.MONGO_DB['scheduled_viva']
        current_date = datetime.now().date()
        classroom_code = request.session.get('classroom_code')
        host_name = request.session.get('username')
        host_id = request.session.get('host_id')

        # Fetch all scheduled viva data
        all_scheduled_viva = schedule_viva_collection.find()
        matching_vivas = schedule_viva_collection.find({'classroom_code': classroom_code})
        viva_data = [
            {
                'id': str(record['_id']),  # Convert ObjectId to string
                **{key: value for key, value in record.items() if key != '_id'}
            }
            for record in matching_vivas
        ]
        past_vivas = [viva for viva in viva_data if datetime.strptime(viva['vivaDate'], "%Y-%m-%d").date() < current_date]
        upcoming_vivas = [viva for viva in viva_data if datetime.strptime(viva['vivaDate'], "%Y-%m-%d").date() >= current_date]

        print(classroom_code)
        print(host_id)
        # Fetch all classrooms matching the filter
        host_classrooms = list(classrooms.find({'host_id': host_id}))
        print(host_classrooms)

        # Prepare context for the template
        context = {
            'classrooms': host_classrooms,  # Pass multiple classrooms
            'past_vivas': past_vivas,
            'upcoming_vivas': upcoming_vivas,
            'host_name': host_name
        }

        return render(request, 'index.html', context)

    except Exception as e:
        # Log the error and return an HTTP response for debugging
        return HttpResponse(f"Error: {str(e)}", content_type="text/plain")


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Required if using JavaScript to send data
def store_classroom_code(request):
    if request.method == 'POST':
        viva_collection = settings.MONGO_DB['scheduled_viva']
        classroom_code = request.POST.get('classroom_code')
        if classroom_code:
            # Store the classroom_code in the session
            request.session['classroom_code'] = classroom_code

            # Query MongoDB for documents matching the classroom_code
            matching_vivas = viva_collection.find({'classroom_code': classroom_code})

            # Convert the results to a list of dictionaries
            viva_list = []
            for viva in matching_vivas:
                viva['_id'] = str(viva['_id'])  # Convert ObjectId to string
                viva_list.append(viva)

            return JsonResponse({'success': True, 'data': viva_list, 'message': 'Classroom code stored and data retrieved.'})
        else:
            return JsonResponse({'success': False, 'message': 'Classroom code is missing.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings

def STDlogin(request):
    collection = settings.MONGO_DB['users']  # Access the MongoDB collection
    
    if request.method == 'POST':
        # Get data from POST request
        full_name = request.POST.get('name')
        er_number = request.POST.get('er-number')  # Match the HTML 'name' attribute
        institute_number = request.POST.get('institute-number')  # Match the HTML 'name' attribute

        # Validate input
        if not (full_name and er_number and institute_number):
            return JsonResponse({'status': 'error', 'message': 'All fields are required'})

        user_id = str(uuid.uuid4())
        # Save to MongoDB
        user_data = {
            '_id': user_id, 
            'role': 'student', 
            'full_name': full_name,
            'er_number': er_number,
            'institute_number': institute_number,
        }
        collection.insert_one(user_data)  # Insert data into MongoDB
        request.session['_id'] = user_id  # Store _id in session
        request.session['role'] = 'student'  # Store _id in session
        request.session['enroll_no'] = er_number  # Store _id in session


        # Redirect to confirmation page
        return render(request, 'STDconf.html', {'user_data': user_data})  # Pass data to the template

    # Render the current form page for non-POST requests
    return render(request, 'STDlogin.html')


def HOSTlogin(request):
    collection = settings.MONGO_DB['hosts']  # Access the MongoDB collection
    
    if request.method == 'POST':
        # Get data from POST request
        full_name = request.POST.get('name')
        role = 'host'
        user_name = request.POST.get('host-name')  # Match the HTML 'name' attribute
        institute_number = request.POST.get('institute-number')  # Match the HTML 'name' attribute

        # Validate input
        if not (full_name and user_name and institute_number):
            return JsonResponse({'status': 'error', 'message': 'All fields are required'})

        user_id = str(uuid.uuid4())
        # Save to MongoDB
        user_data = {
            '_id': user_id, 
            'role': role, 
            'full_name': full_name,
            'user_name': user_name,
            'institute_number': institute_number,
        }
        collection.insert_one(user_data)  # Insert data into MongoDB
        request.session['host_id'] = user_id  # Store _id in session
        request.session['role'] = role # Store _id in session
        request.session['user_data'] = user_data # Store _id in session
        request.session.modified = True


        # Redirect to confirmation page
        return render(request, 'STDconf.html', {'user_data': user_data})  # Pass data to the template

    # Render the current form page for non-POST requests
    return render(request, 'hostlogin.html')

from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings

def STDconf(request):
    # Access MongoDB collections
    users_collection = settings.MONGO_DB['users']
    hosts_collection = settings.MONGO_DB['hosts']

    if request.method == 'POST':
        try:
            # Get data from the POST request
            college_name = request.POST.get('college-name')
            branch = request.POST.get('branch')
            year = request.POST.get('year')

            # Get session data
            user_id = request.session.get('_id')  # For student
            host_id = request.session.get('host_id')  # For host
            role = request.session.get('role')  # Role determines the collection to update

            # Validate required fields
            if not (college_name and branch and year):
                return JsonResponse({'status': 'error', 'message': 'All fields are required.'})

            if not role:
                return JsonResponse({'status': 'error', 'message': 'Role is not defined in session data.'})

            # Prepare query and update data
            query = {'_id': user_id if role == 'student' else host_id}
            update_data = {
                '$set': {
                    'college_name': college_name,
                    'branch': branch,
                    'year': year
                }
            }

            # Choose the correct collection
            collection = hosts_collection if role == 'host' else users_collection

            # Update the document
            result = collection.update_one(query, update_data)
            print("Update result:", result.raw_result)

            if result.matched_count > 0:
                if result.modified_count > 0:
                    return render(request, 'STDpass.html')  # Redirect to success page
                else:
                    return JsonResponse({
                        'status': 'success',
                        'message': 'No changes were made; details are already up-to-date.'
                    })
            else:
                return JsonResponse({'status': 'error', 'message': 'Record not found.'})
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'})

    # Render the form page for non-POST requests
    return render(request, 'STDconf.html')

import random
import re
from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
from pymongo import MongoClient
from bson import ObjectId
import json
from django.contrib.auth.hashers import make_password


# Initialize MongoDB client and collection
# client = MongoClient(settings.MONGO_CLIENT)  # Update with your MongoDB URI
# db = client[settings.MONGO_DB]
otp_collection = settings.MONGO_DB['otp_store']
user_collection = settings.MONGO_DB['users']
host_collection = settings.MONGO_DB['hosts']

# Utility to generate a secure OTP
def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')

        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email is required'})

        # Generate OTP and expiration time
        otp = generate_otp()
        expiration_time = now() + timedelta(minutes=5)

        # Store OTP in MongoDB
        otp_collection.update_one(
            {'email': email},
            {'$set': {'otp': otp, 'expires_at': expiration_time}},
            upsert=True
        )

        # Send email
        try:
            send_mail(
                subject='Your OTP Code',
                message=f'Your OTP code is {otp}. It will expire in 5 minutes.',
                from_email='your-email@gmail.com',  # Replace with your email
                recipient_list=[email],
                fail_silently=False,
            )
            return JsonResponse({'status': 'success', 'message': 'OTP sent successfully'})
        except Exception as e:
            print(f"Error sending email: {e}")
            return JsonResponse({'status': 'error', 'message': 'Failed to send OTP. Please try again.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def verify_otp(request):
    if request.method == 'POST':
        data = json.get(request.body)

        email = data.get('email')
        otp = data.get('otp')


        if not (email and otp):
            return JsonResponse({'status': 'error', 'message': 'Email and OTP are required'})

        # Retrieve OTP from MongoDB
        record = otp_collection.find_one({'email': email})

        if not record or record['otp'] != otp:
            return JsonResponse({'status': 'error', 'message': 'Invalid OTP.'})

        if record['expires_at'] < now():
            otp_collection.delete_one({'email': email})
            return JsonResponse({'status': 'error', 'message': 'OTP expired.'})

        # OTP verified successfully
        otp_collection.delete_one({'email': email})  # Delete OTP after successful verification
        return JsonResponse({'status': 'success', 'message': 'OTP verified successfully!'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

import re
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.hashers import make_password
# from .models import user_collection, host_collection

# def STDpass(request):
#     user_collection = settings.MONGO_DB['users']
#     user_collection = settings.MONGO_DB['hosts']
#     if request.method == 'POST':
#         try:
#             # Get form data from the POST request
#             password = request.POST.get('password')
#             confirm_password = request.POST.get('confirm-password')
#             email = request.POST.get('email')
#             user_id = request.session.get('_id')
#             role = request.session.get('role')

#             # Debugging session data
#             print("Session ID:", user_id)
#             print("Role:", role)

#             # Validate required fields
#             if not (password and confirm_password and email):
#                 return JsonResponse({'status': 'error', 'message': 'All fields are required'})

#             # Validate passwords
#             if password != confirm_password:
#                 return JsonResponse({'status': 'error', 'message': 'Passwords do not match'})

#             # Validate email format
#             email_regex = r'^[\w\.-]+@[\w\.-]+\.\w{2,4}$'
#             if not re.match(email_regex, email):
#                 return JsonResponse({'status': 'error', 'message': 'Invalid email format'})

#             # Hash the password for storage
#             hashed_password = make_password(password)

#             # Ensure user ID is valid from session
#             if not user_id:
#                 return JsonResponse({'status': 'error', 'message': 'Session expired. Please log in again.'})

#             # Prepare the update query for MongoDB
#             update_query = {'_id': user_id}
#             update_data = {'$set': {'password': hashed_password, 'email': email}}

#             # Update the appropriate collection based on user role
#             if role == 'host':
#                 host_collection.update_one(update_query, update_data)
#             else:
#                 user_collection.update_one(update_query, update_data)

#             return render(request, 'landing_page.html')
#             # Check if any records were updated
#             # if result.modified_count > 0:
#             #     return redirect(request, 'Landing_page')  # Redirect to landing page on success
#             # else:
#             #     return JsonResponse({'status': 'error', 'message': 'No changes made to user data'})

#         except Exception as e:
#             print(f"Unexpected error: {e}")
#             return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred. Please try again.'})

#     return render(request, 'std_pass.html')

import re
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings


import re
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings


def STDpass(request):
    # Access MongoDB collections
    user_collection = settings.MONGO_DB['users']
    host_collection = settings.MONGO_DB['hosts']

    if request.method == 'POST':
        try:
            # Extract form data
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm-password')
            email = request.POST.get('email')
            role = request.session.get('role')
            user_id = request.session.get('_id') or request.session.get('host_id')  # Support both roles

            # Validate session and required fields
            if not user_id:
                return JsonResponse({'status': 'error', 'message': 'Session expired. Please log in again.'})

            if not (password and confirm_password and email):
                return JsonResponse({'status': 'error', 'message': 'All fields are required.'})

            if password != confirm_password:
                return JsonResponse({'status': 'error', 'message': 'Passwords do not match.'})

            # Validate email format
            email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_regex, email):
                return JsonResponse({'status': 'error', 'message': 'Invalid email format.'})

            # Hash the password
            hashed_password = make_password(password)

            # Define update query and data
            update_query = {'_id': user_id}
            update_data = {'$set': {'password': hashed_password, 'email': email}}

            # Determine the correct collection
            collection = host_collection if role == 'host' else user_collection

            # Perform the update
            result = collection.update_one(update_query, update_data)

            # Check update result
            if result.matched_count > 0:
                if result.modified_count > 0:
                    return render(request, 'hello.html')  # Redirect on successful update
                return JsonResponse({
                    'status': 'success',
                    'message': 'No changes were necessary; your data is already up-to-date.'
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'No matching user found to update.'})

        except Exception as e:
            # Log the exception (replace print with proper logging)
            print(f"Unexpected error: {e}")
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred. Please try again.'})

    # Render the password update form for non-POST requests
    return render(request, 'std_pass.html')


from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

import pytz
IST = pytz.timezone('Asia/Kolkata')


def STDashboard(request):
    
    from datetime import datetime, timedelta
    from django.utils.timezone import make_aware
    from django.http import JsonResponse
    from django.shortcuts import render
    from django.conf import settings
    print(f'ONGOING VIVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')

    # Access MongoDB collections
    classrooms_collection = settings.MONGO_DB['classrooms']
    viva_collection = settings.MONGO_DB['scheduled_viva']
    user_collection = settings.MONGO_DB['users']
    notifications_collection = settings.MONGO_DB['notifications']
    
    # Retrieve session data
    username = request.session.get('name')
    host_name = request.session.get('user_name')
    user_id = request.session.get('user_id')
    
    # Check if the user is logged in
    if not username or not user_id:
        return JsonResponse({
            "success": False,
            "message": "User is not logged in."
        })
    
    try:
        # Query classrooms where the user is a student
        updated_classroom = list(
            classrooms_collection.find({
                "students": {"$elemMatch": {"id": user_id, "name": username}}
            })
        )

        # Extract classroom codes
        classroom_codes = [classroom["classroom_code"] for classroom in updated_classroom]
        print("Classroom Codes:", classroom_codes)

        # Fetch notifications for all classrooms
        notifications_by_classroom = {}
        for code in classroom_codes:
            notifications = notifications_collection.find({"classroom_code": code})
            notifications_by_classroom[code] = list(notifications)
        
        # Fetch scheduled vivas
        scheduled_vivas = list(
            viva_collection.find({
                "classroom_code": {"$in": classroom_codes}
            })
        )

        # Get the current time (timezone-aware)
        current_time = datetime.now(IST)
        print(f'cccccccccccccccccccccccccccccccccccccccccccccccccurent TIMEEEEEEEEEEEEEEEEEEEEE {current_time}')

        # Filter vivas to get only ongoing ones
        ongoing_vivas = []
        for viva in scheduled_vivas:
            # Parse the viva date and time
            viva_datetime_str = f"{viva['vivaDate']} {viva['vivaTime']}"
            viva_datetime = datetime.strptime(viva_datetime_str, "%Y-%m-%d %H:%M")
            viva_datetime = make_aware(viva_datetime)  # Make it timezone-aware

            # Check if the viva is ongoing
            if viva_datetime <= current_time <= (viva_datetime + timedelta(hours=2)):  # Assuming 2-hour duration
                ongoing_vivas.append(viva)

        # Handle if there are no ongoing vivas
        if ongoing_vivas:
            first_viva = ongoing_vivas[0]
            print(first_viva)
            request.session['ongoing_viva_subjectname'] = first_viva['subjectName']
            request.session['ongoing_viva_classroom_code'] = first_viva['classroom_code']
            request.session['ongoing_viva_total_no'] = first_viva['numQuestions']
        else:
            first_viva = None

        # Render the template with classroom and ongoing viva data
        return render(request, 'STDashboard.html', {
            "classroom": updated_classroom,
            "vivas": ongoing_vivas,
            "username": username,
            "notifications": notifications_by_classroom,
        })
    
    except Exception as e:
        # Log the error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in STDashboard: {str(e)}")
        
        # Return an error response
        return JsonResponse({
            "success": False,
            "message": f"An error occurred: {str(e)}"
        })


def STDprofile(request):
    return render(request, 'STDprofile.html')

def STDanalytics(request):
    return render(request, 'STDanalytics.html')

def Notifications(request):
    return render(request, 'notifications.html')

def Landing_page(request):
    # return render(request, 'landing_page.html')
    return render(request, 'hello.html')

def StdHost(request):
    # return render(request, 'landing_page.html')
    return render(request, 'Host_stud.html')

def StdSignIN(request):
    # return render(request, 'landing_page.html')
    return render(request, 'signINHost.html')

from django.shortcuts import render
from django.conf import settings
from pymongo.errors import PyMongoError











def CreateClassroom(request):
    classrooms = settings.MONGO_DB['classrooms']
    if request.method == 'POST':
        # Get the data from the form
        classroom_name = request.POST.get('classroomName')
        course_code = request.POST.get('courseCode')
        host_id = request.session.get('host_id')
        print(f"Classroom name: {classroom_name}")
        print(f"Coursecode: {course_code}")

        # Validate the data
        if not classroom_name or not course_code:
            return render(request, 'index.html', {'error': 'All fields are required.'})

        classroom_code = generate_classroom_id(classroom_name)
        classroom_data = {
            'classroom_name': classroom_name,
            'course_code': course_code,
            'host_id': host_id,
            'classroom_code': classroom_code,
            'students': [],
        }

        try:
            # Insert the data into MongoDB
            classrooms.insert_one(classroom_data)
            print("Classroom created successfully!")

        except PyMongoError as e:
            # Handle MongoDB-related errors
            print(f"MongoDB error: {e}")
            return render(request, 'index.html', {'error': 'There was an error creating the classroom. Please try again later.'})

        except Exception as e:
            # Catch any other exceptions
            print(f"Unexpected error: {e}")
            return render(request, 'index.html', {'error': 'An unexpected error occurred. Please try again later.'})

        # Redirect to the home view after success
        return redirect('host_dashboard')

    # Render the form if it's a GET request
    return render(request, 'index.html')




from django.http import JsonResponse
from django.shortcuts import render
from django.db import IntegrityError
from django.utils import timezone
# from .models import Question  # Assuming your Question model is in models.py

def generate_viva_session_id():
    import random
    # Generate a random 6-digit number
    session_id = f"VIVA-{random.randint(100000, 999999)}"
    return session_id


def start_session(request):
    request.session['person_warning_count'] = 0
    request.session['cellphone_warning_count'] = 0
    """
    Initialize or fetch the session questions.
    If no questions are stored in the session, it will fetch them from MongoDB
    and store them in the session. It will also handle AJAX requests for fetching 
    individual questions.
    """
    # Check if a session ID already exists; if not, generate one
    if 'viva_session_id' not in request.session:
        viva_session_id = generate_viva_session_id()
        request.session['viva_session_id'] = viva_session_id
        print("Generated new session ID:", viva_session_id)
    else:
        viva_session_id = request.session['viva_session_id']
        print("Using existing session ID:", viva_session_id)

    # Initialize questions in session if not already present
    if 'questions' not in request.session:
        total_questions = request.session.get('ongoing_viva_total_no_new')
        print("Total question no: ",total_questions )
        # Fetch questions from the database or MongoDB
        all_fetched_questions = fetch_questions_from_mongodb(request)  # Replace with actual data fetch function
        if not all_fetched_questions:
            return JsonResponse({'error': 'No questions available'}, status=500)

        # Select random questions (modify the selection logic as needed)
        questions = select_random_questions(all_fetched_questions, total_questions)
        if not questions:
            return JsonResponse({'error': 'Not enough questions selected'}, status=500)

        # Store selected questions in session
        request.session['questions'] = questions
        request.session.modified = True  # Mark the session as modified
        print("New questions saved in session:", questions)
    else:
        questions = request.session['questions']
        print("Questions already in session:", questions)

    # Handle AJAX request for a specific question
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            question_no = int(request.GET.get('question_no', 0))  # Get the requested question number
            if 0 <= question_no < len(questions):
                return JsonResponse({
                    'question': questions[question_no],
                    'current': question_no,
                    'total': len(questions),
                })
            else:
                return JsonResponse({'error': 'Invalid question number'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Question number must be an integer'}, status=400)

    # Render the initial page with questions (non-AJAX requests)
    context = {
        'questions': request.session['questions'],
        'total_questions': len(request.session['questions']),
    }
    return render(request, 'SessionPage.html', context)

from django.http import JsonResponse
from django.shortcuts import render

# def start_session(request):
#     if 'questions' not in request.session:
#         all_questions = fetch_questions_from_mongodb()
#         if not all_questions:
#             return JsonResponse({'error': 'No questions available'}, status=500)

#         # Select 5 random questions
#         request.session['questions'] = select_random_questions(all_questions, 5)
#         request.session.modified = True

#     questions = request.session['questions']
#     question_no = int(request.GET.get('question_no', 0))

#     if 0 <= question_no < len(questions):
#         return JsonResponse({
#             'question': questions[question_no],
#             'current': question_no,
#             'total': len(questions),
#         })
#     return JsonResponse({'error': 'Invalid question number'}, status=400)

# def process_transcript(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         transcript = data.get('transcript')
#         question = data.get('question')

#         # Save to MongoDB
#         save_response_to_mongodb(question, transcript)
#         return JsonResponse({'success': 'Response saved'})
#     return JsonResponse({'error': 'Invalid request'}, status=400)


from django.http import JsonResponse

def end_session(request):
    """
    Handle the end of a session. This will clear the session data when the tab is closed
    or when explicitly called from the client-side (via AJAX).
    """
    # Check if the 'questions' key exists in session before clearing
    if 'questions' in request.session:
        del request.session['questions']
        request.session.modified = True  # Mark session as modified

        print("Session questions data cleared.")

        return JsonResponse({'message': 'Session ended and questions cleared.'}, status=200)
    else:
        return JsonResponse({'error': 'No session data to clear.'}, status=400)

import hashlib
import string

def generate_classroom_id(subject_name):
    """
    Generate a unique classroom ID based on the subject name.

    Parameters:
        subject_name (str): The name of the subject.

    Returns:
        str: A unique classroom ID.
    """
    # Step 1: Create a hash from the subject name
    subject_hash = hashlib.md5(subject_name.encode()).hexdigest()[:6]  # Use the first 6 characters of the hash
    
    # Step 2: Generate a random alphanumeric string for added uniqueness
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    # Step 3: Combine the hash and random string to form the classroom ID
    classroom_id = f"{subject_hash}-{random_suffix}"
    
    return classroom_id

# Example usage
# subject_name = "Mathematics"
# classroom_id = generate_classroom_id(subject_name)
# print(f"Classroom ID for '{subject_name}': {classroom_id}")


# import logging
# logger = logging.getLogger(__name__)
# def start_session(request):
#     try:
#         # Fetch the questions (from session, database, or API)
#         questions = request.session.get('questions', {})
#         question_no = int(request.GET.get('question_no', 1))
        
#         # Debugging logs
#         logger.debug(f"Questions: {questions}")
#         logger.debug(f"Requested question number: {question_no}")

#         # Check if the question exists
#         question = questions.get(question_no)
#         if not question:
#             return JsonResponse({'error': 'Question not found'}, status=404)

#         return JsonResponse({'question': question})
#     except Exception as e:
#         logger.error(f"Error in start_session: {str(e)}")
#         return JsonResponse({'error': 'Internal server error'}, status=500)


######################################################### OPEN CV ##########################################################################

# import cv2
# import numpy as np
# from datetime import datetime
# from deepface import DeepFace
# from ultralytics import YOLO
# import base64
# from django.http import JsonResponse
# from django.shortcuts import render
# import os

# os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# # Load YOLO model and Haar Cascade for face detection
# yolo_model = YOLO("data/yolov8n.pt")
# cascade_path = "data/haarcascade_frontalface_default.xml"
# face_cascade = cv2.CascadeClassifier(cascade_path)


# def decode_frame(encoded_frame):
#     """
#     Decodes a base64-encoded image frame.
#     """
#     frame_data = base64.b64decode(encoded_frame.split(',')[1])
#     np_array = np.frombuffer(frame_data, dtype=np.uint8)
#     frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
#     return frame


# import time

# # Global variables for cooldown tracking
# # Cooldown configurations
# cooldown_time = 5  # Cooldown for object detection warnings in seconds
# brightness_cooldown_time = 5  # Cooldown for brightness warnings in seconds

# # Global timestamps for cooldown
# last_saved_time = 0  # For object detection cooldown
# last_brightness_save_time = 0  # For brightness detection cooldown

# # Warning counters
# person_warning_count = 0
# cellphone_warning_count = 0
# brightness_warning_count = 0
# person_warning_text = ''
# cellphone_warning_text = ''
# brightness_warning_text = ''


# def check_brightness(frame, min_brightness=65, max_brightness=200):
#     """
#     Checks the brightness of the frame and provides feedback.
#     """
#     global last_brightness_save_time, brightness_warning_count
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     avg_brightness = gray.mean()

#     # Get the current time
#     current_time = time.time()

#     if avg_brightness < min_brightness:
#         if current_time - last_brightness_save_time > brightness_cooldown_time:
#             last_brightness_save_time = current_time
#             save_frame(frame, "TooDim")
#             brightness_warning_count += 1
#             brightness_warning_text = 'Too dim, increase lighting.'

#             return "Too dim, increase lighting.", avg_brightness, False
#         else:
#             brightness_warning_text = 'Too dim, recently warned.'
#             return "Too dim, recently warned.", avg_brightness, False
#     elif avg_brightness > max_brightness:
#         if current_time - last_brightness_save_time > brightness_cooldown_time:
#             last_brightness_save_time = current_time
#             save_frame(frame, "TooBright")
#             brightness_warning_count += 1
#             return "Too bright, reduce lighting.", avg_brightness, False
#         else:
#             return "Too bright, recently warned.", avg_brightness, False
#     else:
#         return "Brightness is acceptable.", avg_brightness, True


# def save_frame(frame, reason="Detected"):
#     """
#     Saves the frame to a folder with a reason in the filename.
#     """
#     from datetime import datetime
#     save_folder = "saved_images"
#     os.makedirs(save_folder, exist_ok=True)  # Create the folder if it doesn't exist
#     timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#     filename = os.path.join(save_folder, f"{reason}_image_{timestamp}.jpg")
#     cv2.imwrite(filename, frame)
#     print(f"Image saved as {filename} for reason: {reason}")


# def detect_objects(frame):
#     """
#     Detect objects using YOLO and save images based on specific conditions.
#     """
#     global last_saved_time, person_warning_count, cellphone_warning_count
#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = yolo_model.predict(rgb_frame, conf=0.3, save=False, stream=True)
#     detected_objects = []
#     person_count = 0
#     save_image = False  # Flag to determine if an image should be saved
#     person_warning_msg = ''
#     cellphone_warning_msg = ''


#     for result in results:
#         for box in result.boxes:
#             x1, y1, x2, y2 = map(int, box.xyxy[0])
#             conf = box.conf[0]
#             class_id = int(box.cls[0])
#             label = f"{yolo_model.names[class_id]}: {conf:.2f}"
#             detected_objects.append(label)

#             # Count 'person' objects
#             if yolo_model.names[class_id] == 'person':
#                 person_count += 1

#             # Check for 'cell phone'
#             if yolo_model.names[class_id] == 'cell phone':
#                 save_image = True
#                 cellphone_warning_count += 1
#                 cellphone_warning_msg = 'Cellphone detected, Assure that you are not using any electronic device attending Viva.'

#                 # request.session['cellphone_warning_count'] += 1

    
#     # Increment warning count if more than one person is detected
#     if person_count >= 2:
#         person_warning_count += 1 
#         person_warning_msg = 'More than one person detected, Assure that only one person is attending Viva.'
#          # Increment person warning count
#         # request.session['person_warning_count'] += 1

#     # Check if a save is required based on person count or cellphone detection
#     current_time = time.time()
#     if (person_count >= 2 or save_image) and (current_time - last_saved_time > cooldown_time):
#         last_saved_time = current_time  # Update the last saved time
#         save_frame(frame, "CheatDetected")

#     return detected_objects, person_warning_msg, cellphone_warning_msg


# def analyze_emotions(frame):
#     try:
#         analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False, detector_backend='mtcnn')
#         emotion = analysis[0]['dominant_emotion']
#         score = analysis[0]['emotion'][emotion]
#         return f"Emotion: {emotion}, Confidence: {score:.2f}", emotion, score
#     except Exception as e:
#         return "Emotion detection failed.", None, None


# import time


# import json
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from datetime import datetime

# @csrf_exempt
# def process_frame(request):
#     from datetime import datetime
#     """
#     Process the incoming frame and return analysis results.
#     """
#     try:
#         if request.method == "POST":
#             data = json.loads(request.body)
#             encoded_frame = data.get('frame')  # Safely access 'frame'
#             frame = decode_frame(encoded_frame)

#             # Perform brightness detection
#             brightness_msg, brightness, _ = check_brightness(frame)

#             # Perform emotion detection
#             emotion_msg, emotion, score = analyze_emotions(frame)

#             # Perform object detection
#             detected_objects, person_warning_msg, cellphone_warning_msg = detect_objects(frame)

#             # Log output to the terminal
#             timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#             print(f"\n[{timestamp}]")
#             print(f"Brightness Check: {brightness_msg}")
#             print(f"Emotion Analysis: {emotion_msg}")
#             print(f"Detected Objects: {detected_objects}")

#             # Send JSON response with text warnings
#             return JsonResponse({
#                 "message": "Frame processed successfully.",
#                 "brightness": brightness,
#                 "emotions": emotion_msg,
#                 "detected_objects": detected_objects,
#                 "mean_pixel_value": frame.mean(),
#                 "warning_counts": {
#                     "person_warning": person_warning_msg,
#                     "cellphone_warning": cellphone_warning_msg,
#                     "brightness_warning": brightness_msg
#                 }
#             })

#     except Exception as e:
#         print(f"Error processing frame: {str(e)}")
#         return JsonResponse({"error": str(e)}, status=500)

import cv2
import numpy as np
import os
import time
import base64
import json
from datetime import datetime
from deepface import DeepFace
from ultralytics import YOLO
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import mediapipe as mp

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Load YOLO model and Haar Cascade for face detection
yolo_model = YOLO("data/yolov8n.pt")
cascade_path = "data/haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)

# Mediapipe face mesh setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# Cooldown configurations and global variables
cooldown_time = 5
brightness_cooldown_time = 5
last_saved_time = 0
last_brightness_save_time = 0
person_warning_count = 0
cellphone_warning_count = 0
brightness_warning_count = 0


def decode_frame(encoded_frame):
    frame_data = base64.b64decode(encoded_frame.split(',')[1])
    np_array = np.frombuffer(frame_data, dtype=np.uint8)
    return cv2.imdecode(np_array, cv2.IMREAD_COLOR)


def check_brightness(frame, min_brightness=65, max_brightness=200):
    global last_brightness_save_time, brightness_warning_count
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    avg_brightness = gray.mean()
    current_time = time.time()

    if avg_brightness < min_brightness:
        if current_time - last_brightness_save_time > brightness_cooldown_time:
            last_brightness_save_time = current_time
            save_frame(frame, "TooDim")
            brightness_warning_count += 1
            return "Too dim, increase lighting.", avg_brightness, False
        return "Too dim, recently warned.", avg_brightness, False
    elif avg_brightness > max_brightness:
        if current_time - last_brightness_save_time > brightness_cooldown_time:
            last_brightness_save_time = current_time
            save_frame(frame, "TooBright")
            brightness_warning_count += 1
            return "Too bright, reduce lighting.", avg_brightness, False
        return "Too bright, recently warned.", avg_brightness, False
    return "Brightness is acceptable.", avg_brightness, True


# def save_frame(frame, reason="Detected"):
#     save_folder = "saved_images"
#     os.makedirs(save_folder, exist_ok=True)
#     timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#     filename = os.path.join(save_folder, f"{reason}image{timestamp}.jpg")
#     cv2.imwrite(filename, frame)
#     print(f"Image saved as {filename} for reason: {reason}")

def save_frame(frame, reason="Detected"):
    """
    Saves the frame to a folder with a reason in the filename.
    """
    from datetime import datetime
    save_folder = "saved_images_new"
    os.makedirs(save_folder, exist_ok=True)  # Create the folder if it doesn't exist
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(save_folder, f"{reason}_image_{timestamp}.jpg")
    cv2.imwrite(filename, frame)
    print(f"Image saved as {filename} for reason: {reason}")


def detect_objects(frame):
    
    global last_saved_time, person_warning_count, cellphone_warning_count
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = yolo_model.predict(rgb_frame, conf=0.3, save=False, stream=True)
    detected_objects = []
    person_count = 0
    save_image = False

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_id = int(box.cls[0])
            label = f"{yolo_model.names[class_id]}"
            detected_objects.append(label)

            if label == 'person':
                person_count += 1
            elif label == 'cell phone':
                save_image = True
                cellphone_warning_count += 1

    if person_count >= 2 or save_image:
        if time.time() - last_saved_time > cooldown_time:
            last_saved_time = time.time()
            save_frame(frame, "CheatDetected")
            person_warning_count += 1


    person_warning_msg = 'Multiple persons detected.' if person_count >= 2 else ''
    cellphone_warning_msg = 'Cellphone detected.' if save_image else ''
    return detected_objects, person_warning_msg, cellphone_warning_msg


def analyze_emotions(frame):
    try:
        analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False, detector_backend='mtcnn')
        emotion = analysis[0]['dominant_emotion']
        return f"Emotion: {emotion}", emotion
    except Exception as e:
        return "Emotion detection failed.", None


def process_gaze(frame):
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            left_eye_points = [33, 133, 160, 158, 153, 144]  # Mediapipe indices for left eye
            right_eye_points = [362, 263, 387, 385, 380, 373]  # Mediapipe indices for right eye

            left_eye = [(int(face_landmarks.landmark[i].x * frame.shape[1]),
                         int(face_landmarks.landmark[i].y * frame.shape[0])) for i in left_eye_points]
            right_eye = [(int(face_landmarks.landmark[i].x * frame.shape[1]),
                          int(face_landmarks.landmark[i].y * frame.shape[0])) for i in right_eye_points]

            # Gaze logic: check eye center relative to bounding box
            left_center_x = sum([pt[0] for pt in left_eye]) // len(left_eye)
            left_bbox_width = max(pt[0] for pt in left_eye) - min(pt[0] for pt in left_eye)

            right_center_x = sum([pt[0] for pt in right_eye]) // len(right_eye)
            right_bbox_width = max(pt[0] for pt in right_eye) - min(pt[0] for pt in right_eye)

            if left_center_x < left_bbox_width * 0.4 or right_center_x < right_bbox_width * 0.4:
                return "Left"
            elif left_center_x > left_bbox_width * 0.6 or right_center_x > right_bbox_width * 0.6:
                return "Right"
            else:
                return "Center"
    return "No face detected."


@csrf_exempt
def process_frame(request):
    from datetime import datetime
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            encoded_frame = data.get('frame')
            frame = decode_frame(encoded_frame)

            brightness_msg, _, _ = check_brightness(frame)
            emotion_msg, _ = analyze_emotions(frame)
            detected_objects, person_warning_msg, cellphone_warning_msg = detect_objects(frame)
            gaze_direction = process_gaze(frame)

            # Log output to the terminal
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n[{timestamp}]")
            print(f"Brightness Check: {brightness_msg}")
            print(f"Emotion Analysis: {emotion_msg}")
            print(f"Detected Objects: {detected_objects}")
            print(f"Gaze detection: {gaze_direction}")

            # Initialize warning count in the session if not already set
            if 'warning_count' not in request.session:
                request.session['warning_count'] = 0

            # Count object detection warnings
            warning_count = 0
            print("###Warning count: ", warning_count)
            if person_warning_msg:
                warning_count += 1
            if cellphone_warning_msg:
                warning_count += 1

            # Update session warning count
            request.session['warning_count'] += warning_count

            # Send JSON response with text warnings
            return JsonResponse({
                "message": "Frame processed successfully.",
                "brightness": brightness_msg,
                "emotions": emotion_msg,
                "detected_objects": detected_objects,
                "mean_pixel_value": frame.mean(),
                "warning_counts": {
                    "person_warning": person_warning_msg,
                    "cellphone_warning": cellphone_warning_msg,
                    "brightness_warning": brightness_msg,
                    "Gaze detection":(f"Ensure you looking at center, Dont look {gaze_direction}") 
                }
            })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# from .mongodb_utils import users_collection

from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.hashers import check_password

def user_login(request):
    users_collection = settings.MONGO_DB['users']

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Debugging prints
        print("Email:", email)
        print("Password:", password)
        print("Password:", password)

        if not email or not password:
            messages.error(request, 'Email and password are required.')
            return redirect('login')

        user = users_collection.find_one({"email": email})
        if user:
            if check_password(password, user['password']):
                print("correct Password !!!")
                request.session['user_id'] = str(user['_id'])
                request.session['name'] = user.get('full_name', 'User')

                request.session['role'] = user.get('role', 'student')
                request.session['email'] = user['email']

                next_url = 'STDashboard'
                print("Redirecting to:", next_url)
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid password.')
        else:
            messages.error(request, 'User not found.')

        return redirect('STDashboard')

    return render(request, 'login.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.hashers import check_password

def hosts_login(request):
    # Access the MongoDB collection for host users
    hosts_collection = settings.MONGO_DB['hosts']

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Validate input fields
        if not username or not password:
            messages.error(request, 'Both username and password are required.')
            return redirect('hosts_login')  # Ensure this matches your URL name

        # Query the database for the username
        host_user = hosts_collection.find_one({"user_name": username})

        if host_user:
            # Validate the password (assumes passwords are stored hashed)
            if check_password(password, host_user['password']):
                # Store user details in the session
                request.session['host_id'] = str(host_user['_id'])
                request.session['username'] = host_user['user_name']
                request.session['role'] = 'host'

                # Redirect to the host dashboard or desired page
                return redirect('host_dashboard')  # Replace 'dashboard' with the host-specific page
            else:
                messages.error(request, 'Invalid password.')
        else:
            messages.error(request, 'Host not found.')

        # Redirect back to login on failure
        return redirect('hosts_login')

    return render(request, 'HOST_login.html')  # ✅ CORRECT



def user_logout(request):
    request.session.flush()  # Clear the session
    return redirect('login')

@login_required
def dashboard(request):
    role = request.session.get('role')
    if role == 'student':
        return render(request, 'dashboard.html', {"message": "Welcome to the Student Dashboard"})
    elif role == 'host':
        return render(request, 'dashboard.html', {"message": "Welcome to the Host Dashboard"})
    else:
        return render(request, 'dashboard.html', {"message": "Dashboard"})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings

@csrf_exempt
def join_classroom(request):
    if request.method == "POST":
        try:
            # Get student data from session
            user_id = request.session.get("user_id")
            email = request.session.get("email")
            name = request.session.get("name")

            if not user_id or not email:
                return JsonResponse({"success": False, "message": "User is not logged in."})

            # Parse classroom code from the request
            data = json.loads(request.body)
            classroom_code = data.get("classroom_code")
            request.session['classroom_code'] = classroom_code
            print()
            print(classroom_code)

            if not classroom_code:
                return JsonResponse({"success": False, "message": "Classroom code is required."})

            # Access MongoDB collections
            db = settings.MONGO_DB
            classrooms_collection = db["classrooms"]
            users_collection = db["users"]

            print(classrooms_collection)

            # Find the classroom by code
            classroom = classrooms_collection.find_one({"classroom_code": classroom_code})
            print("Classrooms fetched: ", classroom)
            if not classroom:
                return JsonResponse({"success": False, "message": "Invalid classroom code."})

            # Check if the student is already in the classroom
            students = classroom.get("students", [])
            if any(student["id"] == user_id for student in students):
                return JsonResponse({"success": False, "message": "Student already added to the classroom."})

            # Add the student to the classroom
            new_student = {
                "id": user_id,
                "name": name,
                "email": email
            }
            result = classrooms_collection.update_one(
                {"classroom_code": classroom_code},
                {"$addToSet": {"students": new_student}}  # Avoid duplicates
            )

            print("result: ", result)

            # Add the classroom code to the user's document
            users_collection.update_one(
                {"_id": user_id},
                {"$addToSet": {"classrooms": classroom_code}}  # Prevent duplicate codes
            )

            # Fetch the updated classroom details
            # updated_classroom = list(classrooms_collection.find({"classroom_code": classroom_code}))
            # print(updated_classroom)

            # # Render the template with the specific classroom details
            # return render(request, 'STDashboard.html', {"classroom": updated_classroom})
            return JsonResponse({
                "success": True,
                "message": "Classroom retrieved successfully.",
                
    })

        except Exception as e:
            return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

    return JsonResponse({"success": False, "message": "Invalid request method."})

from django.http import JsonResponse
from pymongo import MongoClient

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient
import json

from django.http import JsonResponse
from pymongo import MongoClient
import json
import datetime

from django.http import JsonResponse
from pymongo import MongoClient
import datetime

@csrf_exempt  # Disables CSRF validation for this view (use carefully)
def store_transcripts_to_mongo(request):
    if request.method == 'POST' or 'GET':
        try:
            # Get viva_session_id from session
            viva_session_id = request.session.get('viva_session_id')
            print(f"Session Viva Session ID: {viva_session_id}")
            
            if not viva_session_id:
                return JsonResponse({'error': 'Viva session ID is missing from session.'}, status=400)

            # MongoDB setup
            client = MongoClient("mongodb+srv://shree:shree%401234@cluster0.fhplq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
            db = client["Viva_Viva_Online_db"]
            conducted_viva_collection = db["transcripts"]
            consolidated_viva_collection = db["consolidated_viva"]

            # Fetch data from conducted_viva collection
            viva_data = list(conducted_viva_collection.find({"session_id": viva_session_id}))
            print(f"Fetched Viva Data: {viva_data}")

            if not viva_data:
                return JsonResponse({'error': 'No data found for the provided viva session ID.'}, status=404)
            # score = item.get("evaluation_score")
            # if score == None:
            #     score=0

            # Prepare consolidated data
            consolidated_data = {
                "viva_session_id": viva_session_id,
                "timestamp": datetime.datetime.now(),
                "questions_and_answers": [
                    {
                        "question": item.get("question"),
                        "transcript": item.get("transcript"),
                        "evaluation_score": item.get("evaluation_score"),
                        "timestamp": item.get("timestamp", datetime.datetime.now())
                    }
                    for item in viva_data
                ]
            }

            # Save to consolidated_viva collection
            consolidated_viva_collection.insert_one(consolidated_data)
            print(f"Consolidated Viva Data Saved: {consolidated_data}")
            

            return render(request, 'submissionPage.html')

        except Exception as e:
            print(f"Unexpected Error: {e}")
            return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)

    return JsonResponse({'error': 'Invalid method. Only POST allowed.'}, status=405)

def score_aggregation(response_scores,  warning):
    """
    Calculate final viva score based on responses, confidence, and monitoring violations.
    
    Parameters:
    response_scores (list): List of scores (0-10) for each response
    confidence_scores (list): List of confidence percentages for each response
    multiple_persons_count (int): Number of times multiple persons were detected
    unauthorized_objects_count (int): Number of unauthorized objects detected
    
    Returns:
    tuple: (final_score, confidence_message)
    """
    

    # Validate inputs
    # if not response_scores or not confidence_scores:
    #     raise ValueError("Must provide at least one response score and confidence score")
    
    # Constants for scoring weights
    RESPONSE_WEIGHT = 0.7
    MONITORING_WEIGHT = 0.3
    
    # Warning penalties
    WARNING_PENALTY = 1.0
    
    # Calculate response score (0-10)
    avg_response_score = sum(response_scores) / len(response_scores) if response_scores else 0
    
    # Calculate average confidence
    # avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    avg_confidence = 90

    
    # Calculate monitoring penalties
    total_penalty = warning*WARNING_PENALTY
    print("total penalty: ", total_penalty)
    
    # Cap monitoring penalty at 10 and calculate monitoring score
    monitoring_penalty = min(total_penalty, 10)
    monitoring_score = 10 - monitoring_penalty
    
    # Calculate initial weighted score
    initial_score = (
        (avg_response_score * RESPONSE_WEIGHT) +
        (monitoring_score * MONITORING_WEIGHT)
    )
    print("Initial Score: ", initial_score)
    # Add confidence bonus if average confidence is above 85%
    adjusted_score = initial_score
    confidence_message = ""
    if avg_confidence > 85:
        adjusted_score += 1.0
        confidence_message = f"Bonus marks added! Average confidence ({avg_confidence:.1f}%) was above 85%"
    else:
        confidence_message = f"No bonus marks. Average confidence ({avg_confidence:.1f}%) was below 85%"
    
    print("Adjusted Score: ", adjusted_score)
    # Ensure final score is between 0 and 10
    final_score = min(max(round(adjusted_score, 2), 0), 10)
    
    return final_score, confidence_message

# Example usage
# if _name_ == "_main_":
#     response_scores = [9, 5, 7, 8, 6, 7]
#     confidence_scores = [88, 88, 90, 87, 99, 67,55,88,34]  
#     warning = 1

# response_scores = get_evaluation_scores()
# final_score, confidence_msg = score_aggregation(
#         response_scores,
#         confidence_scores,
#         warning
#     )
# print(f"Final Score: {final_score}")
# print(confidence_msg)

from pymongo import MongoClient

def get_evaluation_scores(viva_session_id):
    """
    Retrieve the evaluation scores for each question and answer pair from MongoDB.
    
    Args:
        viva_session_id (str): The session ID for which scores are to be fetched.

    Returns:
        list: A list of evaluation scores, or an error message if the session is not found.
    """
    try:
        # Connect to MongoDB
        transcripts_collection = settings.MONGO_DB["consolidated_viva"]  # Replace with your collection name

        # Query the document using the viva_session_id
        record = transcripts_collection.find_one({"viva_session_id": viva_session_id})

        # Handle case where no document is found
        if not record:
            return {"error": "No data found for the provided viva session ID."}

        # Extract evaluation scores
        questions_and_answers = record.get("questions_and_answers", [])
        scores = [qa.get("evaluation_score") for qa in questions_and_answers]

        print(len(scores))
        for i in range(0, len(scores)):
            if scores[i] == None:
                scores[i] = 1

        print(scores[-1])
        return scores

    except Exception as e:
        print(f"Error: {e}")
        return {"error": "An unexpected error occurred while fetching evaluation scores."}

# Example usage
# viva_session_id = "VIVA-486980"
# scores = get_evaluation_scores(viva_session_id)
# print(scores)

def FinalScore(request):
    viva_session_id = request.session.get('viva_session_id')
    print(viva_session_id)
    person_warning = request.session.get('person_warning_count')
    cellphone_warning = request.session.get('cellphone_warning_count')
    # warning_count = person_warning_count + brightness_warning_count + cellphone_warning_count
    warning_count = request.session.get('warning_count')
    print("Warning Count: ",warning_count)
    scores = get_evaluation_scores(viva_session_id)
    print(scores)
    final_score = score_aggregation(scores, warning_count)
    print(final_score)
    print(type(final_score), final_score)

    # Convert final_score to a valid type if necessary
    if isinstance(final_score, set):
        final_score = list(final_score)  # Convert set to list

    
#     # username = request.session.get('name')
#     # enrollment_no = request.session.get('ernroll_no')
#     user_id = request.session.get('_id')
#     classroom_code = request.session.get('classroom_code')

#     user_collection = settings.MONGO_DB['users']
#     user = user_collection.find({'_id': user_id})
#     classroom_collection = settings.MONGO_DB['classrooms']
#     user_classroom = classroom_collection.find({'_id': user_id})

#     classroom = classroom_collection.find({'classroom_code': classroom_code})
#     host_collection= settings.MONGO_DB['hosts']

#     user_collection = settings.MONGO_DB['users']

#     host_id = request.session.get('host_id')
#     host_data = host_collection.find({'_id': host_id})
    
#     questions_collection = settings.MONGO_DB['consolidated_viva']
#     question = questions_collection.find({'viva_session_id': viva_session_id})
    

#     # viva_session_id = request.session.get('_id')

#     data = {
#     "username": user['full_name'],
#     "enrollment_no": user['er_number'],
#     "branch": user['branch'],
#     "year": user['year'],
#     "classroom_code": classroom_code ,
#     "subject_code": classroom['course_code'],
#     "subject": classroom['classroom_name'],
#     "faculty_name": host_data['full_name'],




#     "questions_answers": [
#         # {"question": question['questions_and_answers'][0].get('question'), "answer":question['questions_and_answers'][0].get('transcript')},
#         {"question": "Define machine learning.", "answer": "Machine learning is a subset of AI which deals with complex models and algorithms that involves machine to learn certain patterns."},
#         {"question": "What is deep learning?", "answer": "Deep learning is a type of machine learning that uses neural networks with many layers."},
#         {"question": "Explain supervised learning.", "answer": "Supervised learning involves training a model on labeled data to make predictions or classifications."},
#         {"question": "What is natural language processing?", "answer": "Natural Language Processing (NLP) is a field of AI that enables computers to understand, interpret, and respond to human languages."},
#     ],
#     "warnings": [
#         {"warning": "Detected head movement away from the screen.", "timestamp": "2024-11-24 12:00:00"},
#         {"warning": "Unauthorized activity detected.", "timestamp": "2024-11-24 12:05:00"},
#     ],
#     "score": final_score # Example aggregated score
# }
    from bson import ObjectId, errors

# Extract session variables
    user_id = request.session.get('user_id')
    classroom_code = request.session.get('classroom_code')
    print("Classroom code: ", classroom_code)
    host_id = request.session.get('host_id')
    viva_session_id = request.session.get('viva_session_id')  # Ensure it's set

    # Connect to MongoDB collections
    user_collection = settings.MONGO_DB['users']
    classroom_collection = settings.MONGO_DB['classrooms']
    host_collection = settings.MONGO_DB['hosts']
    questions_collection = settings.MONGO_DB['consolidated_viva']

    # Safe ObjectId conversion
    def safe_objectid(value):
        try:
            print(value)
            return ObjectId(value)
        except (errors.InvalidId, TypeError):
            return None

    # Fetch data from the database
    user = user_collection.find_one({'_id': user_id}) if user_id else None
    # user_classroom = classroom_collection.find_one({'_id': safe_objectid(user_id)}) if user_id else None
    classroom = classroom_collection.find_one({'classroom_code': classroom_code}) if classroom_code else None
    host_data = host_collection.find_one({'_id':host_id}) if host_id else None
    question = questions_collection.find_one({'viva_session_id': viva_session_id}) if viva_session_id else None

    # Prepare response data
    data = {
        "username": user.get('full_name', 'N/A') if user else 'N/A',
        "enrollment_no": user.get('er_number', 'N/A') if user else 'N/A',
        "branch": user.get('branch', 'N/A') if user else 'N/A',
        "year": user.get('year', 'N/A') if user else 'N/A',
        "classroom_code": classroom_code,
        "subject_code": classroom.get('course_code', 'N/A') if classroom else 'N/A',
        "subject": classroom.get('classroom_name', 'N/A') if classroom else 'N/A',
        "faculty_name": host_data.get('full_name', 'N/A') if host_data else 'N/A',
        "questions_answers": [
            {"question": qa.get('question', 'N/A'), "answer": qa.get('transcript', 'N/A')}
            for qa in (question.get('questions_and_answers', []) if question else [])
        ], 
        "scores": scores,
        
        "warnings": [
            {"warning": "Detected head movement away from the screen.", "timestamp": "2024-11-24 12:00:00"},
            {"warning": "Unauthorized activity detected.", "timestamp": "2024-11-24 12:05:00"},
        ],
        "score": final_score if 'final_score' in locals() else 'N/A'  # Ensure final_score is defined
    }

    report_collection = settings.MONGO_DB['student_report']
    report_collection.insert_one(data)


    generate_pdf_report(data, r'media\DataRepo\ram\Material\STDREPORT\report.pdf')

    # current_subjectname = classroom.get('classroom_name')
    current_subjectname = 'test_subject'
    # filename = f'media\DataRepo\ram\Material\STDREPORT\{current_subjectname}.csv'
    generate_csv_report(data, r'media\DataRepo\ram\Material\STDREPORT\New_csv_report.csv')

    return render(request, 'STDashboard.html')


from fpdf import FPDF
def generate_pdf_report(data, output_path):
    class PDF(FPDF):
        def add_page_border(self):
            self.set_draw_color(0, 0, 0)  # Black color for the border
            self.rect(5, 5, 200, 287)  # Draw the border (adjust dimensions if needed)

        def header(self):
            # Add page border
            self.add_page_border()

            # Add logo to the top-right corner
            self.image(r'media\DataRepo\ram\Material\logo\logo.jpg', 160, 5, 40)  # Adjust position and size as needed

            # Set Montserrat font for user details
            self.add_font('Montserrat', '', r'media\DataRepo\ram\Material\font\Montserrat-Regular.ttf', uni=True)
            self.set_font('Montserrat', '', 10)

            # Add user details in two columns side by side
            self.cell(95, 10, f"Username: {data['username']}", ln=False)
            self.cell(95, 10, f"Class Code: {data['classroom_code']}", ln=True)

            self.cell(95, 10, f"Enrollment No: {data['enrollment_no']}", ln=False)
            self.cell(95, 10, f"Subject Code: {data['subject_code']}", ln=True)

            self.cell(95, 10, f"Branch: {data['branch']}", ln=False)
            self.cell(95, 10, f"Subject: {data['subject']}", ln=True)

            self.cell(95, 10, f"Year: {data['year']}", ln=False)
            self.cell(95, 10, f"Faculty Name: {data['faculty_name']}", ln=True)

            # Draw a horizontal line
            self.ln(5)
            self.set_draw_color(0, 0, 0)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(10)

        def footer(self):
            # Position at 1.5 cm from bottom
            self.set_y(-15)
            # Add page number
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', align='C')

    # Create instance of PDF class
    pdf = PDF()
    pdf.add_page()

    # Add Q&A section
    pdf.set_font('Times', 'B', 12)
    pdf.cell(0, 10, "Session Info:", ln=True)
    pdf.set_font('Times', '', 12)
    for i, qa in enumerate(data["questions_answers"], start=1):
        pdf.cell(0, 10, f"{i}) Question: {qa['question']}", ln=True)
        pdf.multi_cell(0, 10, f"   Answer: {qa['answer']}")
    pdf.ln(10)

    # Add warnings section as a table
    pdf.set_font('Times', 'B', 12)
    pdf.cell(0, 10, "Warnings (with timestamps):", ln=True)
    pdf.set_font('Times', 'B', 10)
    pdf.cell(140, 8, "Warning", border=1, align='L')
    pdf.cell(50, 8, "Timestamp", border=1, align='L', ln=True)
    pdf.set_font('Times', '', 10)
    for warning in data["warnings"]:
        pdf.cell(140, 8, warning["warning"], border=1, align='L')
        pdf.cell(50, 8, warning["timestamp"], border=1, align='L', ln=True)
    pdf.ln(10)

    # Add aggregated score section
    pdf.set_font('Times', 'B', 12)
    pdf.cell(0, 10, "Aggregated Score:", ln=True)
    pdf.set_font('Times', '', 12)
    pdf.cell(0, 10, f"The aggregated score of the student is: {data['score']}%", ln=True)
    pdf.ln(10)

    # Save PDF
    pdf.output(output_path)
    print(f"PDF report saved as {output_path}")



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest

@csrf_exempt
def Viva_selection(request):
    if request.method == 'POST':
        try:
            # Parse JSON body
            data = json.loads(request.body)
            parameter_value = data.get('parameter_name')
            another_value = data.get('another_parameter')

            # Validate the parameters
            if not parameter_value or not another_value:
                return HttpResponseBadRequest("Missing required parameters in the request body.")

            # Store in session
            request.session['ongoing_viva_subjectname_new'] = parameter_value
            request.session['ongoing_viva_total_no_new'] = int(another_value)

            # Redirect to another page
            return JsonResponse({"redirect_url": "/start_session/"})
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON body.")
    else:
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)

# Example data
# data = {
#     "username": "testuser",
#     "enrollment_no": "123456",
#     "branch": "Computer Engineering",
#     "year": "Third Year",
#     "class_code": "CSE3A",
#     "subject_code": "AI101x",
#     "subject": "Artificial Intelligence",
#     "faculty_name": "Dr. John Doe",
#     "questions_answers": [
#         {"question": "What is AI?", "answer": "AI stands for Artificial Intelligence."},
#         {"question": "Define machine learning.", "answer": "Machine learning is a subset of AI which deals with complex models and algorithms that involves machine to learn certain patterns."},
#         {"question": "What is deep learning?", "answer": "Deep learning is a type of machine learning that uses neural networks with many layers."},
#         {"question": "Explain supervised learning.", "answer": "Supervised learning involves training a model on labeled data to make predictions or classifications."},
#         {"question": "What is natural language processing?", "answer": "Natural Language Processing (NLP) is a field of AI that enables computers to understand, interpret, and respond to human languages."},
#     ],
#     "warnings": [
#         {"warning": "Detected head movement away from the screen.", "timestamp": "2024-11-24 12:00:00"},
#         {"warning": "Unauthorized activity detected.", "timestamp": "2024-11-24 12:05:00"},
#     ],
#     "score": 85  # Example aggregated score
# }

# Generate the PDF report
# generate_pdf_report(data, "PDF_Report/analysis_report.pdf")

import csv
import os

def generate_csv_report(data, output_path):
    # Check if the file exists
    file_exists = os.path.exists(output_path)
    max_questions = 0  # Track the maximum number of questions
    
    # Read existing data to determine max_questions
    existing_enrollment_numbers = set()
    if file_exists:
        with open(output_path, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                existing_enrollment_numbers.add(row["Enrollment No"])
            # Count dynamic question columns
            max_questions = (len(reader.fieldnames) - 10) // 3  # Adjust to count Q/A/Score groups
    
    # Skip adding data if enrollment number already exists
    if data["enrollment_no"] in existing_enrollment_numbers:
        print(f"Data for Enrollment No {data['enrollment_no']} already exists. Skipping...")
        return
    
    # Update max_questions if new data has more questions
    max_questions = max(max_questions, len(data["questions_answers"]))
    
    # Calculate the aggregated score as the average of scores in the separate list
    scores = data["scores"]
    aggregated_score = sum(scores) / len(scores) if scores else 0  # Avoid division by zero
    
    # Write or append data
    with open(output_path, mode='a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        
        # Write the header only if the file doesn't exist
        if not file_exists:
            header = [
                "Enrollment No", "Class Code", "Username", "Branch", "Year", 
                "Subject Code", "Subject", "Faculty Name"
            ]
            # Add dynamic columns for questions, responses, and scores
            for i in range(1, max_questions + 1):
                header.append(f"Question No {i}")
                header.append(f"Response (Question {i})")
                header.append(f"Score (Question {i})")
            header.append("Warnings with Timestamp")
            header.append("Aggregated Score")
            writer.writerow(header)
        
        # Prepare a row for the user data
        row = [
            data["enrollment_no"],
            data["classroom_code"],
            data["username"],
            data["branch"],
            data["year"],
            data["subject_code"],
            data["subject"],
            data["faculty_name"]
        ]
        
        # Add dynamic question/answer/score data
        for i, qa in enumerate(data["questions_answers"]):
            row.append(qa["question"])
            row.append(qa["answer"])
            row.append(data["scores"][i])  # Retrieve the score from the separate list
        
        # Fill empty columns for missing questions
        for _ in range(len(data["questions_answers"]), max_questions):
            row.extend(["", "", ""])  # Empty question, answer, and score columns
        
        # Add warnings with timestamps (combine into a single string)
        warnings_str = "; ".join([f"{w['warning']} ({w['timestamp']})" for w in data["warnings"]])
        row.append(warnings_str)
        
        # Add aggregated score
        row.append(round(aggregated_score, 2))  # Rounded to two decimal places
        
        # Write the row to the file
        writer.writerow(row)
    
    print(f"Data for Enrollment No {data['enrollment_no']} saved to {output_path}")


# Example data with scores in a separate list
# data = {
#     "username": "student1",
#     "enrollment_no": "2021002",
#     "branch": "Computer Engineering",
#     "year": "Third Year",
#     "class_code": "CSE3A",
#     "subject_code": "AI101",
#     "subject": "Artificial Intelligence",
#     "faculty_name": "Prof. Jane Smith",
#     "questions_answers": [
#         {"question": "What is AI?", "answer": "AI stands for Artificial Intelligence."},
#         {"question": "Define machine learning.", "answer": "It involves algorithms to learn patterns."},
#         {"question": "What is deep learning?", "answer": "It uses neural networks with many layers."},
#         {"question": "Explain supervised learning.", "answer": "It uses labeled data for training."},
#         {"question": "What is NLP?", "answer": "It helps computers understand human languages."},
#     ],
#     "scores": [10, 9, 8, 7, 10],  # Scores in a separate list
#     "warnings": [
#         {"warning": "Detected phone usage.", "timestamp": "2024-12-02 10:15:00"},
#         {"warning": "Prolonged inactivity.", "timestamp": "2024-12-02 10:20:00"},
#     ],
# }

# subject_name = "Artificial_Intelligence"
# filename = f"{subject_name}_scores_data.csv"

# # Generate the CSV report
# generate_csv_report(data, filename)