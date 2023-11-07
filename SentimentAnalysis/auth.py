from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
import requests, boto3, bcrypt

auth = Blueprint('auth', __name__)
dynamodb = boto3.resource('dynamodb',aws_access_key_id='',aws_secret_access_key='', region_name='us-west-1')
table = dynamodb.Table('userdata')

"""
Login Processing
"""
#Added 'Post' method to allowable methods.
@auth.route('/login', methods=['POST', 'GET'])
def login():

    #If request is post process form data.
    if request.method == "POST":
        ##Store form data
        username = request.form['username']
        password = request.form['password']

        response = table.get_item(Key={'username': username})
        if 'Item' in response:
            stored_hashed_password = response['Item']['password']
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                session['username'] = username
                session['logged_in'] = True
                #redirect to Main page with user's name on top of main page.
                return redirect(url_for('views.home'))
            else:
                return render_template('login.html', error='Incorrect username or password. Please try again.')
        else:
            return render_template('login.html', error='User does not exist. Please sign up first.')
    else:
        if( (session.get('logged_in') != None) & (session.get('logged_in') == True)): #if logged in session redirect to home
            return redirect(url_for('views.home'))
        else:
        #DEFAULT PATH: head to login page.
            return render_template('login.html', error=None)

@auth.route('/logout')
def logout():
    ## ON LOGOUT REMOVE SESSION DATA
    session["logged_in"] = False
    session["username"] = ""

    return redirect(url_for('auth.login'))

"""
    DEBUG GO BACK. NOT FINAL
"""
@auth.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        response = table.query(
            KeyConditionExpression='username = :username',
            ExpressionAttributeValues={':username': username}
        )
        if len(response['Items']) == 0:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            table.put_item(
                Item={
                    'username': username,
                    'email': email,
                    'password': hashed_password.decode('utf-8')
                    }
            )
            return render_template('login.html')
        else:
            return render_template('signup.html', username=False)
    else:
        return render_template('signup.html', username=True)

@auth.route('/recovery')
def accountRecover():
    return "<p>recovery</p><form method='GET', action='/login'><input type='submit' value='GO BACK'></form>"