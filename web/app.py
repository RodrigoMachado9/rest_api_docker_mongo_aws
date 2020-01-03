from bottle import response, request, run, error, get, post
from json import dumps
from pymongo import MongoClient


client = MongoClient("mongodb://mongo:27017")
db = client.dockerDB
user_num = db["user_num"]

user_num.insert({
    "num_of_users": 0
})


@get('/')
def hello():
    status = response.status_code
    prev_num = user_num.find({})[0]["num_of_users"]
    new_num = prev_num + 1
    user_num.update({}, { "$set": {"num_of_users": new_num}})
    return {"status": status,
            "message": "Hello user number: %s" % new_num}

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
