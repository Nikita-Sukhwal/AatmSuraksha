from flask import Flask, render_template, request, url_for, redirect, session
import pymongo
import mail
from location import lat, log #, location, city, state
import messagebird
import credentials

#set app as a Flask instance 
app = Flask(__name__)

#encryption relies on secret keys so they could be run
app.secret_key = "testing"
#connoct to your Mongo DB database
client = pymongo.MongoClient("mongodb+srv://Nikita_s:Niki1@cluster0.f9eaa.mongodb.net/Project0?retryWrites=true&w=majority")

#get the database name
db = client.get_database('totalrecords')
#get the particular collection that contains the data
records = db.register

#assign URLs to have a particular route 
@app.route("/", methods=['post', 'get'])
def index():
    message = ''
    #if method post in index
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        #if found in database showcase that it's found 
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        #if user_found:
        #    message = 'There already is a user by that name'
        #    return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            #hash the password and encode it
            #hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            #assing them in a dictionary in key value pairs
            user_input = {'name': user, 'email': email, 'password': password2,'user_emails':" ",'user_phones':" "}
            #insert it in the record collection
            records.insert_one(user_input)
            
            #find the new created account and its email
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
            #if registered redirect to logged in as the registered user
            return render_template('logged_in.html', email=new_email)
    return render_template('index.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        print(email,password)
        #check if email exists in database
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            #encode the password and check if it matches
            #if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
            if(passwordcheck == password):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')


@app.route('/addUsers')
def addUsers():
    return render_template('addTrustedUsers.html')

     
@app.route('/addedUsers', methods=['POST'])
def addedUsers():
    #if request.method == 'POST':
    # Get the file from post request
    if "email" in session:
        email = session["email"]
        
        user_emails = request.form.get('email_usr')
        print(user_emails)

        user_phones = request.form.get('phone_usr')
        print(user_phones)

        

        email_object =  records.find_one({"email": email})
        records.update_one({"_id": email_object['_id']}, {"$set": {"user_emails": user_emails}})
        records.update_one({"_id": email_object['_id']}, {"$set": {"user_phones": user_phones}})

    return render_template('logged_in.html')

@app.route("/emergency", methods=["POST", "GET"])
def emergency():
    if "email" in session:
        email = session["email"]
        email_object =  records.find_one({"email": email})
        name = email_object["name"]
        
	#Get Link to Location using GeoLocation if no gps, uses IP
        link = "http://www.google.com/maps/place/"+lat+","+log
	
	# Sending a call on a helpline number and leaving voice message
        client = messagebird.Client(credentials.CALL_API)
        try:
        	voice_message = "I am "+name+' It is Emergency, Help immediately'+" check my location on sms"
        	msg = client.voice_message_create(credentials.Helpline_no, voice_message,{ 'voice' : 'female' })

        except messagebird.client.ErrorException as e:
        	for error in e.errors:
        		print(error)
	
	# Get Trusted Emails and Send an Email with Location
        list_emails = email_object["user_emails"].split(',')

        for contacts in list_emails:
        	mail.send_email(name,contacts,link)
	
	#Sending SMS to stored contacts but since Testing API Key available only to your own number for now
        list_phones = email_object["user_phones"].split(',')

        for contacts in list_phones:
		try:
        		message = "I am "+name+' It is Emergency, Help immediately '+" check my location- "+link
        		msg = client.message_create(name,contacts,message)
        		print(msg.__dict__)

        	except messagebird.client.ErrorException as e:
        		for error in e.errors:
        			print(error)
				
	#SEE YOUR OWN LOCATION
	return render_template('Location.html')





if __name__ == "__main__":
  app.run(debug=True)
