from bottle import response, request, run, error, get, post
from pymongo import MongoClient
from passlib.hash import bcrypt
from json import dumps
import json, subprocess


# instance of mongodb
client = MongoClient("mongodb://mongo:27017")

db = client.dockerDB
user_num = db["user_num"]     # instance of collections one
user_num.insert({
    "num_of_users": 0
})

db = client.sentence_database
users = db["users"]     # instance of collections two

db = client.image_recognition
users_recognition = db["users_recognition"]     # instance of collections two



def verify_credentials(username, password):
    if not user_exists(username):
        return generate_dictionary(301, "Ivalida username"), True
    correct_password = verify_password(username, password)
    if not correct_password:
        return generate_dictionary(302, "Invalid password"), True
    return None, False

def generate_dictionary(status, message):
    return {"sratus": status, "message": message}

@post('/classify_image')
def classify_image():
    posted_data = request.json

    username = posted_data["username"]
    password = posted_data["password"]
    url = posted_data["url"]

    #todo: verify_credentials
    return_json, error = verify_credentials(username, password)
    if error:
        return {return_json}

    tokens = users.find({"username": username}[0]["tokens"])
    #todo: generate_dictionary
    if tokens <= 0:
        return generate_dictionary(303, "not enougth tokens!")

    r = request.get(url)
    json_msg = {}
    with open("temp.jpg", "wb") as f:
        f.write(r.content)
        proc = subprocess.Popen("python classify_image.py --model_dir=. --image_file=./temp.jpg")
        proc.communicate()[0]
        proc.wait()
        with open("text.txt") as g:
            return json.load(g)

    users.update({
        "username": username
    },
        {"$set": {
            "tokens": tokens - 1
        }})
    return json_msg

@post('/refil')
def refil():
    posted_data = request.json
    username = posted_data["username"]
    password = posted_data["admin_passworld"]
    amount = posted_data["amount"]


    if not user_exists(username):
        return generate_dictionary(301, "Invalid username")

    correct_password = "xyz123"
    if password != correct_password:
        return generate_dictionary(301, "Invalid administrator password")

    users.update({
        "username": username
    }, {"$set": {
        "tokens": amount
    }})
    return generate_dictionary(200, "refilled successfuly")


# http://www.mindrot.org/projects/py-bcrypt/
# https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html
# pip install passlib
@post('/register')
def register():
    api_key = request.params.get('api_key', request.headers.get('x-api-key'))
    status = response.status_code
    posted_data = request.json

    # get data
    username = posted_data["username"]
    password = posted_data["password"]
    # hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
    hashed_password = bcrypt.hash(password)

    if not api_key:
        data_json = {
            "username": username,
            "password": hashed_password,
            "sentence": "",
            "tokens": 6
        }
        with open("teste", "w") as outfile:
            json.dump(data_json, outfile)

    if user_exists(username):
        return {"status": 301,
                "message": "this document of user: %s exists..." % username}

    users.insert({
        "username": username,
        "password": hashed_password,
        "sentence": "",
        "tokens": 6
    })


    if status == 200:
        return {"status": status,
                "message": "success "}
    if status == 500:
        return {"status": status,
                "message": "server internal error"}
    if status == 404:
        return {"status": status,
                "message": "error, page not found"}
    return {"status": status,
            "message": "unexpected error"}

def user_exists(username: str):
    check_user = users.find({"username": username}).count()
    if check_user == 0:
        return False
    return True

@post('/recognition')
def recognition():
    posted_data = request.json

    username = posted_data["username"]
    password = posted_data["passworld"]
    if user_exists(username):
        return {"status": 500,
                "message": "this document of user: %s exists..." % username}

    # generate hash of password
    hashed_password = bcrypt.hash(password)
    users.insert({
        "username": username,
        "password": hashed_password,
        "tokens": 4
    })

    return {"status": 200,
            "message": "you successfully signed up for this api"}


@post('/store')
def store():
    posted_data = request.json

    # read payload data
    username = posted_data["username"]
    password = posted_data["passworld"]
    sentence = posted_data["sentence"]

    # verify data (match)
    correct_password = verify_password(username, password)
    if not correct_password:
        status = response.status_code = 302
        return {"status": status, "message": "login is fail"}

    num_tokens = get_token(username)
    if num_tokens <= 0:
        status = response.status_code = 301
        return {"status": status, "message": "token is fail"}
    users.update({
        "username": username,
    }, {"$set": {"sentence": sentence,
                 "tokens": num_tokens}})

    status = response.status_code = 200
    return {"status": status, "message": "sentence save successfully!!"}


def verify_password(username, password):
    hashed_password = users.find({
        "username": username,
    })[0]["password"]
    if bcrypt.verify(password, hashed_password):
        return True
    return False

def get_token(username):
    tokens = users.find({
        "username": username
    })[0]["tokens"]
    if tokens:
        return tokens
    return None



@get('/hithere')
def hi_there_everyone():
    return "I just hit /hithere"

@get('/consult')
def bye():
    # prepare a response for the request that came to /bye
    c = 2*534
    s = str(c)
    data = {
        "status": str(response.status_code),
        "message": "the result operation is: %s " % s,
        "phones": [
            {
                "phoneName": "my-iphone",
                "phoneNumber": "11952841555",
                "isActivated": None
            },
            {
                "phoneName": "my-android",
                "phoneNumber": "11952841555",
                "isActivated": None
            }

        ]
    }
    response.content_type = 'application/json'
    return dumps(data)

@post('/sum_two_nums')
def sum_two_nums():
    response.content_type = 'application/json'
    data: dict = request.json
    x = data.get("number_one", 0)
    y = data.get("number_two", 0)
    return dumps({"is_sum_numbers": {
        "number_one": x,
        "number_two": y,
        "result_sum": x + y
    }})

@post('/division_two_nums')
def divide_two_nums():
    response.content_type = 'application/json'
    data: dict = request.json
    x = data.get("number_one", 0)
    y = data.get("number_two", 0)
    return dumps({"is_sum_numbers": {
        "number_one": x,
        "number_two": y,
        "result_sum": x / y
    }})


@post('/multiply_two_nums')
def divide_two_nums():
    response.content_type = 'application/json'
    data: dict = request.json
    x = data.get("number_one", 0)
    y = data.get("number_two", 0)
    return dumps({"is_sum_numbers": {
        "number_one": x,
        "number_two": y,
        "result_sum": x * y
    }})

@get('/')
def hello():
    status = response.status_code
    prev_num = user_num.find({})[0]["num_of_users"]
    new_num = prev_num + 1
    user_num.update({}, {"$set": {"num_of_users": new_num}})
    return {"status": status,
            "message": "Hello user number: %s" % new_num}


@error(404)
def error404(error):
    return '<h1>You have experience a 404</h1>'


@error(500)
def error500(error):
    return '<h1>You have experience a 404</h1>'


if __name__ == '__main__':
    run(host="0.0.0.0", port=8080, debug=True, reload=True)
