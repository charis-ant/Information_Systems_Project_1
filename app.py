from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
import uuid
import time

# Connect to our local MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Choose database
db = client['InfoSys']

# Choose collections
students = db['Students']
users = db['Users']

# Initiate Flask App
app = Flask(__name__)

users_sessions = {}

def create_session(username):
    user_uuid = str(uuid.uuid1())
    users_sessions[user_uuid] = (username, time.time())
    return user_uuid  

def is_session_valid(user_uuid):
    return user_uuid in users_sessions

# ΕΡΩΤΗΜΑ 1: Δημιουργία χρήστη
@app.route('/createUser', methods=['POST'])
def create_user():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "username" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    """
        Το συγκεκριμένο endpoint θα δέχεται στο body του request του χρήστη ένα json της μορφής: 

        {
            "usename": "some username", 
            "password": "a very secure password"
        }

        * Θα πρέπει να εισαχθεί ένας νέος χρήστης στο σύστημα, ο οποίος θα εισάγεται στο collection Users (μέσω της μεταβλητής users). 
        * Η εισαγωγή του νέου χρήστη, θα γίνεται μόνο στη περίπτωση που δεν υπάρχει ήδη κάποιος χρήστης με το ίδιο username. 
        * Αν γίνει εισαγωγή του χρήστη στη ΒΔ, να επιστρέφεται μήνυμα με status code 200. 
        * Διαφορετικά, να επιστρέφεται μήνυμα λάθους, με status code 400.
    """

    #Checking if the count for the given data is zero, which means there was no user with the same username
    if users.find({"username":data["username"]}).count() == 0:
        #Passing the login information to dictionary user
        user = {"username":data['username'], "password":data['password']}
        #Inserting user to database
        users.insert_one(user)
        #Success response if the query executed successfully and user was added to database
        return Response(data['username']+" was added to the MongoDB", status=200, mimetype='application/json')
    #A user with the same username was found
    else:
        #Error response if a user with the same username already exist
        return Response("A user with the given username already exists", status=400, mimetype='application/json')
    

# ΕΡΩΤΗΜΑ 2: Login στο σύστημα
@app.route('/login', methods=['POST'])
def login():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "username" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    """
        Να καλεστεί η συνάρτηση create_session() (!!! Η ΣΥΝΑΡΤΗΣΗ create_session() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) 
        με παράμετρο το username μόνο στη περίπτωση που τα στοιχεία που έχουν δοθεί είναι σωστά, δηλαδή:
        * το data['username'] είναι ίσο με το username που είναι στη ΒΔ (να γίνει αναζήτηση στο collection Users) ΚΑΙ
        * το data['password'] είναι ίσο με το password του συγκεκριμένου χρήστη.
        * Η συνάρτηση create_session() θα επιστρέφει ένα string το οποίο θα πρέπει να αναθέσετε σε μία μεταβλητή που θα ονομάζεται user_uuid.
        
        * Αν γίνει αυθεντικοποίηση του χρήστη, να επιστρέφεται μήνυμα με status code 200. 
        * Διαφορετικά, να επιστρέφεται μήνυμα λάθους με status code 400.
    """

    #Checking if user with the given username and password exists
    if users.find_one({"$and":[ {"username":data['username']}, {"password":data['password']}]}):
        #Calling function create_session and passing its return value to variable user_uuid 
        user_uuid = create_session(data['username'])
        #Passing the user's uuid and username information to dictionary res
        res = {"uuid": user_uuid, "username": data['username']}
        #Success response containing phrase "Successful login" alongside user's uuid and username
        return Response("Successful login "+ json.dumps(res),status=200, mimetype='application/json')
    #Authentication failed
    else:
        #Error response if user's information are not correct
        return Response("Wrong username or password.", status=400, mimetype='application/json')

# ΕΡΩΤΗΜΑ 3: Επιστροφή φοιτητή βάσει email 
@app.route('/getStudent', methods=['GET'])
def get_student():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 

        Το συγκεκριμένο endpoint θα δέχεται σαν argument το email του φοιτητή και θα επιστρέφει τα δεδομένα του. 
        Να περάσετε τα δεδομένα του φοιτητή σε ένα dictionary που θα ονομάζεται student.
        
        Σε περίπτωση που δε βρεθεί κάποιος φοιτητής, να επιστρέφεται ανάλογο μήνυμα.
    """

    #Passing users's uuid to variable uuid
    uuid = request.headers.get('authorization')
    #Calling function is_session_valid with parameter uuid and passing its rerurn value to variable authentication
    authentication = is_session_valid(uuid)
    #Authentication failed
    if (authentication == False):
        #Error response
        return Response("Authentication Failed", status=401, mimetype='application/json')
    #Authentication successful
    else:
        #Searching in students collection for a student with the given email and passing the result to dictionary student
        student = students.find_one({"email":data['email']})
        #Checking if student with the given email exists
        if student != None:
            #Setting key student _id to null in order to print student's data in line 154
            student['_id'] = None
            #Success response containing student's info
            return Response(json.dumps(student), status=200, mimetype='application/json')
        #Response if student with given email doesn't exist
        return Response('No student with that email was found',status=500,mimetype='application/json')
    
# ΕΡΩΤΗΜΑ 4: Επιστροφή όλων των φοιτητών που είναι 30 ετών
@app.route('/getStudents/thirties', methods=['GET'])
def get_students_thirty():

    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 
        
        Το συγκεκριμένο endpoint θα πρέπει να επιστρέφει τη λίστα των φοιτητών οι οποίοι είναι 30 ετών.
        Να περάσετε τα δεδομένα των φοιτητών σε μία λίστα που θα ονομάζεται students.
        
        Σε περίπτωση που δε βρεθεί κάποιος φοιτητής, να επιστρέφεται ανάλογο μήνυμα και όχι κενή λίστα.
    """

    #Passing users's uuid to variable uuid
    uuid = request.headers.get('authorization')
    #Calling function is_session_valid with parameter uuid and passing its rerurn value to variable authentication
    authentication = is_session_valid(uuid)
    #Authentication failed
    if (authentication == False):
        #Error response
        return Response("Authentication Failed", status=401, mimetype='application/json')
    #Authentication successful
    else:
        #Checking if the count for students born in the year 1991 is zero, which means there are no students born in that year
        if (students.find({"yearOfBirth":{"$eq":1991}}).count() == 0):
            #Response if no student born in 1991 was found
            return Response("No students born in 1991 were found", mimetype='application/json')
        #There are students in the database born in the year 1991
        else:
            #Passing the result of the search in students collection for the students born in 1991
            iterable = students.find({"yearOfBirth":{"$eq":1991}})
            #Creating an empty students_list (not students beacause that is the name of the collection)
            students_list = []
            #For every student found
            for student in iterable:
                #Setting key student _id to null in order to print student's data in line 203
                student['_id'] = None 
                #Adding student's info to students_list
                students_list.append(student)
        #Success response containing every student's (in student_list) info
        return Response(json.dumps(students_list), status=200, mimetype='application/json')
        
# ΕΡΩΤΗΜΑ 5: Επιστροφή όλων των φοιτητών που είναι τουλάχιστον 30 ετών
@app.route('/getStudents/oldies', methods=['GET'])
def get_students_oldy():

    """  
        Στα headers του request ο χρήστης θα πρέπει να περνάει και το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 
        
        Το συγκεκριμένο endpoint θα πρέπει να επιστρέφει τη λίστα των φοιτητών οι οποίοι είναι 30 ετών και άνω.
        Να περάσετε τα δεδομένα των φοιτητών σε μία λίστα που θα ονομάζεται students.
        
        Σε περίπτωση που δε βρεθεί κάποιος φοιτητής, να επιστρέφεται ανάλογο μήνυμα και όχι κενή λίστα.
    """
    #Passing users's uuid to variable uuid
    uuid = request.headers.get('authorization')
    #Calling function is_session_valid with parameter uuid and passing its rerurn value to variable authentication
    authentication = is_session_valid(uuid)
    #Authentication failed
    if (authentication == False):
        #Error response
        return Response("Authentication Failed", status=401, mimetype='application/json')
    #Authentication successful
    else:
        #Checking if the count for students born in the year 1991 or earlier is zero, which means there are no students born in that year or before it
        if (students.find({"yearOfBirth":{"$lte":1991}}).count() == 0):
            #Response if no student born in 1991 or earlier was found
            return Response("No students born in or before 1991 were found", mimetype='application/json')
        else:
            #Passing the result of the search in students collection for the students born in 1991 or earlier
            iterable = students.find({"yearOfBirth":{"$lte":1991}})
            #Creating an empty students_list (not students beacause that is the name of the collection)
            students_list = []
            #For every student found
            for student in iterable:
                #Setting key student _id to null in order to print student's data in line 247
                student['_id'] = None 
                 #Adding student's info to students_list
                students_list.append(student)
            #Success response containing every student's (in student_list) info
        return Response(json.dumps(students_list), status=200, mimetype='application/json')

# ΕΡΩΤΗΜΑ 6: Επιστροφή φοιτητή που έχει δηλώσει κατοικία βάσει email 
@app.route('/getStudentAddress', methods=['GET'])
def get_student_address():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει και το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 

        Το συγκεκριμένο endpoint θα δέχεται σαν argument το email του φοιτητή. 
        * Στη περίπτωση που ο φοιτητής έχει δηλωμένη τη κατοικία του, θα πρέπει να επιστρέφεται το όνομα του φοιτητή η διεύθυνσή του(street) και ο Ταχυδρομικός Κωδικός (postcode) της διεύθυνσης αυτής.
        * Στη περίπτωη που είτε ο φοιτητής δεν έχει δηλωμένη κατοικία, είτε δεν υπάρχει φοιτητής με αυτό το email στο σύστημα, να επιστρέφεται μήνυμα λάθους. 
        
        Αν υπάρχει όντως ο φοιτητής με δηλωμένη κατοικία, να περάσετε τα δεδομένα του σε ένα dictionary που θα ονομάζεται student.
        Το student{} να είναι της μορφής: 
        student = {"name": "Student's name", "street": "The street where the student lives", "postcode": 11111}
    """
    #Passing users's uuid to variable uuid
    uuid = request.headers.get('authorization')
    #Calling function is_session_valid with parameter uuid and passing its rerurn value to variable authentication
    authentication = is_session_valid(uuid)
    #Authentication failed
    if (authentication == False):
        #Error response
        return Response("Authentication Failed", status=401, mimetype='application/json')
    #Authentication successful
    else:
        #Checking if there is any student in the database with the given email and their address stated
        student = students.find_one({"$and":[{"address":{"$ne":None}},{"email":data['email']}]})
        #Checking if student exist
        if student != None:
            #Passing student's info (name, street and postcode) to dictionary student
            student = {"name":student['name'],"street":student['address'][0]['street'], "postcode":student['address'][0]['postcode']}
            #Success response containing student's info
            return Response(json.dumps(student), status=200, mimetype='application/json')
        #There is no student found
        else:
            #Response if no student was found
            return Response('No student was found',status=500,mimetype='application/json')


# ΕΡΩΤΗΜΑ 7: Διαγραφή φοιτητή βάσει email 
@app.route('/deleteStudent', methods=['DELETE'])
def delete_student():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει και το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 

        Το συγκεκριμένο endpoint θα δέχεται σαν argument το email του φοιτητή. 
        * Στη περίπτωση που υπάρχει φοιτητής με αυτό το email, να διαγράφεται από τη ΒΔ. Να επιστρέφεται μήνυμα επιτυχούς διαγραφής του φοιτητή.
        * Διαφορετικά, να επιστρέφεται μήνυμα λάθους. 
        
        Και στις δύο περιπτώσεις, να δημιουργήσετε μία μεταβλήτη msg (String), η οποία θα περιλαμβάνει το αντίστοιχο μήνυμα.
        Αν βρεθεί ο φοιτητής και διαγραφεί, στο μήνυμα θα πρέπει να δηλώνεται και το όνομά του (πχ: msg = "Morton Fitzgerald was deleted.").
    """

    #Passing users's uuid to variable uuid
    uuid = request.headers.get('authorization')
    #Calling function is_session_valid with parameter uuid and passing its rerurn value to variable authentication
    authentication = is_session_valid(uuid)
    #Authentication failed
    if (authentication == False):
        #Error response
        return Response("Authentication Failed", status=401, mimetype='application/json')
    #Authentication successful
    else:
        #Searching in students collection for a student with the given email and passing the result to dictionary student 
        student = students.find_one({"email":data['email']})
        #Checking if the student with the given email exists
        if student != None:
            #Deleting the student from the collection
            students.delete_one(student)
            #Passing the student's name and the string " was deleted" to variable msg
            msg = student['name'] + " was deleted"
            #Response if query executed successfully
            return Response(msg, status=200, mimetype='application/json')
        #There is no student with the given email
        else:
            #Response if there is no student with the given email
            return Response("No student with that email was found", status=500, mimetype='application/json')

# ΕΡΩΤΗΜΑ 8: Εισαγωγή μαθημάτων σε φοιτητή βάσει email 
@app.route('/addCourses', methods=['PATCH'])
def add_courses():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "courses" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει και το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 

        Το συγκεκριμένο endpoint θα δέχεται σαν argument το email του φοιτητή. Στο body του request θα πρέπει δίνεται ένα json της παρακάτω μορφής:
        
        {
            email: "an email",
            courses: [
                {'course 1': 10}, 
                {'course 2': 3 }, 
                {'course 3': 8},
                ...
            ]
        } 
        
        Η λίστα courses έχει μία σειρά από dictionary για τα οποία τα key αντιστοιχούν σε τίτλο μαθημάτων και το value στο βαθμό που έχει λάβει ο φοιτητής σε αυτό το μάθημα.
        * Στη περίπτωση που υπάρχει φοιτητής με αυτό το email, θα πρέπει να γίνει εισαγωγή των μαθημάτων και των βαθμών τους, σε ένα νέο key του document του φοιτητή που θα ονομάζεται courses. 
        * Το νέο αυτό key θα πρέπει να είναι μία λίστα από dictionary.
        * Αν δε βρεθεί φοιτητής με αυτό το email να επιστρέφεται μήνυμα λάθους. 
    """
    #Passing users's uuid to variable uuid
    uuid = request.headers.get('authorization')
    #Calling function is_session_valid with parameter uuid and passing its rerurn value to variable authentication
    authentication = is_session_valid(uuid)
    #Authentication failed
    if (authentication == False):
        #Error response
        return Response("Authentication Failed", status=401, mimetype='application/json')
    #Authentication successful
    else:
        #Searching in students collection for a student with the given email and passing the result to dictionary student
        student = students.find_one({"email":data['email']})
        #Checking if the student with the given email exists
        if student != None:
            #Updating the student by adding the courses information
            students.update_one({"email":data['email']}, 
                {"$set":
                     {
                        "courses":data['courses']
                    }
                })
            #Passing the student's name and the string " was updated" to variable msg
            msg = student['name'] + " was updated"
            #Response if query executed successfully
            return Response(msg, status=200, mimetype='application/json')
        #There is no student with the given email
        else:
            #Response if there is no student with the given email
            return Response("No student with that email was found", status=500, mimetype='application/json')
    

# ΕΡΩΤΗΜΑ 9: Επιστροφή περασμένων μαθημάτων φοιτητή βάσει email
@app.route('/getPassedCourses', methods=['GET'])
def get_courses():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    """    Στα headers του request ο χρήστης θα πρέπει να περνάει και το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 

        Το συγκεκριμένο endpoint θα δέχεται σαν argument το email του φοιτητή.
        * Στη περίπτωση που ο φοιτητής έχει βαθμολογία σε κάποια μαθήματα, θα πρέπει να επιστρέφεται το όνομά του (name) καθώς και τα μαθήματα που έχει πέρασει.
        * Στη περίπτωη που είτε ο φοιτητής δεν περάσει κάποιο μάθημα, είτε δεν υπάρχει φοιτητής με αυτό το email στο σύστημα, να επιστρέφεται μήνυμα λάθους.
        
        Αν υπάρχει όντως ο φοιτητής με βαθμολογίες σε κάποια μαθήματα, να περάσετε τα δεδομένα του σε ένα dictionary που θα ονομάζεται student.
        Το dictionary student θα πρέπει να είναι της μορφής: student = {"course name 1": X1, "course name 2": X2, ...}, όπου X1, X2, ... οι βαθμολογίες (integer) των μαθημάτων στα αντίστοιχα μαθήματα.
    """
    
    #Passing users's uuid to variable uuid
    uuid = request.headers.get('authorization')
    #Calling function is_session_valid with parameter uuid and passing its rerurn value to variable authentication
    authentication = is_session_valid(uuid)
    #Authentication failed
    if (authentication == False):
        #Error response
        return Response("Authentication Failed", status=401, mimetype='application/json')
    #Authentication successful
    else:
        #Searching in students collection for a student with the given email and passing the result to dictionary temp
        temp = students.find_one({"$and":[{"courses":{"$ne":None}},{"email":data['email']}]})
        #Checking if the student with the given email exists
        if temp != None:
            #Initializing variable counter (used to check if there are passed courses for the specific) with zero 
            counter = 0
            #Creating empty dictionary student
            student = {}
            #For every course in courses
            for i in temp['courses']:
                #Finding the key's name (the course's name)
                key = list(i.keys())[0]
                #If the value (grade) of the key (course) is greater or equal to five
                if i.get(key) >= 5:
                    #Adding to variable counter because the student has passed at least one course
                    counter = counter + 1
                    #Adding the student to the dictionary student
                    student.update(i)
            #The student has not passed any course
            if counter == 0:
                #Response if the student has not passed any course
                return Response("No passed courses found", status=500, mimetype='application/json')
            #The student has passed at least one course
            else:
                #Response containing student's name and passed courses alongside their grade
                return Response(temp['name'] + ": " + json.dumps(student), status=200, mimetype='application/json')
        #There is no student with the given email
        else:
            #Response if there is no student with the given email
            return Response("No student with that email was found", status=500, mimetype='application/json')

# Εκτέλεση flask service σε debug mode, στην port 5000. 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)