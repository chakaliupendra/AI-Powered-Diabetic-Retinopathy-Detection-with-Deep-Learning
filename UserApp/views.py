

# genai.configure(api_key="AIzaSyAMnuiOxnEEOa_4iCwsFPNUq6fbYrIrYDU")

from google import genai
client = genai.Client(api_key='AIzaSyBgPnsT89URIL-nFOQHBIy3QfQqQ9eSAi4')


from django.shortcuts import render
import sqlite3
import joblib
from django.core.files.storage import FileSystemStorage
import cv2
import imutils
from tensorflow.keras.utils import load_img, img_to_array
from keras.models import Sequential
from keras.layers import Convolution2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense,Dropout
from django.http import JsonResponse
import json
import os
import numpy as np
from django.views.decorators.csrf import csrf_exempt

def index(request):
    return render(request, "UserApp/index.html")

def login(request):
    return render(request, "UserApp/Login.html")
def create_user_table():
    con = sqlite3.connect("brainstroke.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        name varchar(100),
        email varchar(100),
        mobile varchar(100),
        address varchar(100),
        username varchar(100),
        password varchar(100)
    )
    """)
    con.commit()
    con.close()

def loglction(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    con = sqlite3.connect("brainstroke.db")
    cur = con.cursor()

    cur.execute(
        "SELECT * FROM user WHERE username=? AND password=?",
        (username, password)
    )

    data = cur.fetchone()

    if data:
        request.session['user'] = username
        request.session['userid'] = data[0]
        return render(request, 'UserApp/UserHome.html')
    else:
        context = {'data': 'Login Failed ....!!'}
        return render(request, 'UserApp/Login.html', context)

def userhome(request):
    return render(request,'UserApp/UserHome.html')

def register(request):
    return render(request, "UserApp/Register.html")
def regaction(request):
    name = request.POST['name']
    email = request.POST['email']
    mobile = request.POST['mobile']
    address = request.POST['address']
    username = request.POST['username']
    password = request.POST['password']

    con = sqlite3.connect("brainstroke.db")
    cur = con.cursor()

    i = cur.execute("""
        INSERT INTO user (name,email,mobile,address,username,password)
        VALUES (?,?,?,?,?,?)
    """, (name, email, mobile, address, username, password))

    con.commit()
    con.close()

    if i.rowcount == 0:
        context = {'data': 'Registration Failed...!!'}
    else:
        context = {'data': 'Registration Successful...!!'}

    return render(request, 'UserApp/Register.html', context)

def viewprofile(request):
    uid=str(request.session['userid'])
    con = sqlite3.connect("brainstroke.db")
    cur=con.cursor()
    cur.execute("select * from user where id='"+uid+"'")
    data=cur.fetchall()
    strdata="<table border=1><tr><th>Name</th><th>Email</th><th>Mobile</th><th>Address</th><th>Username</th></tr>"
    for i in data:
        strdata+="<tr><td>"+str(i[1])+"</td><td>"+str(i[2])+"</td><td>"+str(i[3])+"</td><td>"+str(i[4])+"</td><td>"+str(i[5])+"</td></tr>"
    context={'data':strdata}
    return render(request,'UserApp/ViewProfile.html',context)

def uploadImage(request):
    return render(request,'UserApp/Upload.html')


global filename, uploaded_file_url

def imageAction(request):
    global filename, uploaded_file_url

    if request.method == 'POST' and request.FILES['image']:
        myfile = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)

        context = {
            'data': 'Test Image Uploaded Successfully',
            'image_url': uploaded_file_url
        }
        return render(request, 'UserApp/Upload.html', context)

    return render(request, 'UserApp/Upload.html')
def brainstrokepredict(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Load image
    path = BASE_DIR + uploaded_file_url

    imagetest = load_img(path, target_size=(48, 48))
    imagetest = img_to_array(imagetest)

    imagetest = np.expand_dims(imagetest, axis=0)

    # Load model
    classifier = Sequential()
    classifier.add(Convolution2D(32, (3, 3), activation='relu', input_shape=(48, 48, 3)))
    classifier.add(MaxPooling2D((2, 2)))
    classifier.add(Convolution2D(32, (3, 3), activation='relu'))
    classifier.add(MaxPooling2D((2, 2)))
    classifier.add(Flatten())
    classifier.add(Dense(128, activation="relu"))
    classifier.add(Dense(4, activation="softmax"))
    classifier.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    classifier.load_weights('model/retinopathy_model.h5')

    pred = classifier.predict(imagetest)
    predict = np.argmax(pred)

    if predict == 0:
        data = "Diabetic Retinopathy Predicted"
    elif predict == 1:
        data = "Macular Edema Predicted"
    elif predict == 2:
        data = "No Diabetic Retinopathy Predicted"
    else:
        data = "No Macular Edema"

    # Read original image
    img = cv2.imread(BASE_DIR + uploaded_file_url)
    output = imutils.resize(img, width=400)

    # Draw rectangle
    (h, w) = output.shape[:2]
    cv2.rectangle(
        output,
        (int(w * 0.3), int(h * 0.3)),
        (int(w * 0.7), int(h * 0.7)),
        (0, 255, 0),
        2
    )

    # Add label
    cv2.putText(output, data, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # Save output image
    result_path = BASE_DIR + "/media/result.jpg"
    cv2.imwrite(result_path, output)

    return render(request, 'UserApp/UserHome.html', {
        'result': data,
        'result_image': '/media/result.jpg'
    })


def chatbot_page(request):
    return render(request,'UserApp/chatbot.html')


@csrf_exempt
def chatbot(request):

    if request.method == "POST":

        data = json.loads(request.body)
        user_message = data.get("message")

        try:

            prompt = f"""
          You are an AI healthcare assistant for diabetic patients.

            Your goal is to give short, relevant, and meaningful responses.

            Conversation Rules:
            - Respond in ONE line whenever possible.
            - Only answer what the user asked (no extra explanation).
            - Keep answers simple, clear, and human-like.
            - Avoid medical jargon unless necessary.
            - Do not give long paragraphs.
            - Use a friendly, conversational tone.
            - Remember previous messages in the conversation.
            - Use past context to avoid repeating information.
            - If the user asks a follow-up, respond based on earlier messages.
            - Do not restart explanations unless asked.
            - Avoid sounding like a textbook.

            Response Rules:
            - Respond in ONE line whenever possible.
            - Only answer what the user asked (no extra explanation).
            - If the user asks about precautions, give 2–3 short points.
            - Keep answers simple, clear, and human-like.
            - Avoid medical jargon unless necessary.

           Scope:
            You can help with:
            - diabetic retinopathy
            - blood sugar control
            - diet recommendations
            - exercise
            - when to consult a doctor

            If the question is unrelated to diabetes, reply:
            "I can only help with diabetes-related questions."

            Patient Question:
            {user_message}
            """

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            reply = response.text

        except Exception as e:
            print(e)
            reply = "Sorry, the AI assistant is currently unavailable."

        return JsonResponse({"reply": reply})