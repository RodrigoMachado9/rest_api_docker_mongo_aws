from bottle import response, request, run, error, get, post
from pymongo import MongoClient
from passlib.hash import bcrypt
from json import dumps
# import bcrypt

# instance of mongodb
client = MongoClient("mongodb://mongo:27017")

db = client.dockerDB
user_num = db["user_num"]     # instance of collections one
user_num.insert({
    "num_of_users": 0
})


db = client.sentence_database
users = db["users"]     # instance of collections two


@get('/')
def hello():
    status = response.status_code
    prev_num = user_num.find({})[0]["num_of_users"]
    new_num = prev_num + 1
    user_num.update({}, {"$set": {"num_of_users": new_num}})
    return {"status": status,
            "message": "Hello user number: %s" % new_num}

# http://www.mindrot.org/projects/py-bcrypt/
# https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html
# pip install passlib

@post('/register')
def register():
    status = response.status_code
    posted_data = request.json

    # get data
    username = posted_data["username"]
    password = posted_data["password"]
    # hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
    hashed_password = bcrypt.hash(password)

    users.insert({
        "username": username,
        "password": hashed_password,
        "sentence": "",
        "tokens": 6
    })

    if status == 200:
        return {"status": status,
                "message": "success"}
    if status == 500:
        return {"status": status,
                "message": "server internal error"}
    if status == 404:
        return {"status": status,
                "message": "error, page not found"}
    return {"status": status,
            "message": "unexpected error"}

@post('/')
def store():
    posted_data = request.json

    # read payload data
    username = posted_data["username"]
    password = posted_data["passworld"]
    sentence = posted_data["sentence"]

    # verify data (match)
    correct_password = verify_login(username, password)
    if not correct_password:
        status = response.status_code = 302
        return {"status": status, "message": "login is fail"}

    num_tokens = count_tokens()
    if num_tokens <= 0:
        status = response.status_code = 301
        return {"status": status, "message": "token is fail"}

    users.update({
        "username": username,
    }, {"$set": {"sentence": sentence,
                 "tokens": num_tokens}})

    status = response.status_code = 200
    return {"status": status, "message": "sentence save successfully!!"}


def verify_login(username, password):
    return True

def count_tokens():
    return 2

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


@error(404)
def error404(error):
    return '<h1>You have experience a 404</h1>'


@error(500)
def error500(error):
    return '<h1>You have experience a 404</h1>'



if __name__ == '__main__':
    run(host="0.0.0.0", port=8080, debug=True, reload=True)
