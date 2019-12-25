from bottle import response, run, error, get
from json import dumps

@get('/')
def hello():
    status = response.status_code
    return {"status": status, "message": "success"}

@get('/hithere')
def hi_there_everyone():
    return "I just hit /hithere"

@get('/multiplication')
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

@error(404)
def error404(error):
    return '<h1>You have experience a 404</h1>'


@error(500)
def error500(error):
    return '<h1>You have experience a 404</h1>'



if __name__ == '__main__':
    run(debug=True, reload=True, port=8080)
