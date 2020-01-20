from bottle_resource import BottleResource, api, api_get, api_post, api_put, api_patch, api_delete
from bottle import response, request, run, error, get, post
from pymongo import MongoClient
from passlib.hash import bcrypt
from bottle import Bottle
import json, subprocess
from json import dumps

# class DemoResource(BottleResource):
#
#     @api('/demos')
#     def get_demo_list(self):
#         return {'demos': [1, 2, 3, 4, 5]}
#
#     @api_get('/demos/<demo_id>')
#     def get_demo_detail(self, demo_id):
#         return {'name': 'demo', 'id': demo_id}
#
#     @api_post('/demos')
#     def create_demo(self):
#         return {'status': 'ok', 'msg': 'created success'}
#
#     @api_put('/demos/<demo_id>')
#     def update_demo(self, demo_id):
#         return {'status': 'ok', 'msg': 'updated success', 'id': demo_id}
#
#     @api_patch('/demos/<demo_id>')
#     def patch_demo(self, demo_id):
#         return {'status': 'ok', 'msg': 'patch success', 'id': demo_id}
#
#     @api_delete('/demos/<demo_id>')
#     def delete_demo(self, demo_id):
#         return {'status': 'ok', 'msg': 'delete success', 'id': demo_id}


# instance of mongodb
client = MongoClient("mongodb://mongo:27017")
db = client.dockerDB
user_num = db["user_num"]  # instance of collections one
user_num.insert({
    "num_of_users": 0
})

db = client.sentence_database
users = db["users"]  # instance of collections two

db = client.image_recognition
users_recognition = db["users_recognition"]  # instance of collections two


# https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html
class Register(BottleResource):

    @api('/')
    def __index__(self):
        return self.status_generate(200, "be welcome!")

    @api_post("/register")
    def register(self):
        posted_data = request.json
        # get of data's payload body
        username = posted_data.get("username")
        password = posted_data.get("password")

        hashed_password = bcrypt.hash(password)
        users.insert({
            "username": username,
            "password": hashed_password,
            "sentence": "",
            "tokens": 10
        })
        return self.status_generate(200, "you successfully signed up for the API !!!")

    def status_generate(self, status: int, message: str):
        return {"status": status,
                "message": message}


class Store(BottleResource):

    def verify_password(self, username, password):
        hashed_password = users.find({
            "username": username
        })[0]["password"]
        is_equal = True if bcrypt.verify(password, hashed_password) else False
        return is_equal

    def count_tokens(self, username):
        tokens = users.find({"username": username})[0]["tokens"]
        return tokens

    def status_generate(self, status: int, message: str = None):
        return {"status": status,
                "message": message}

    @api_post("/store")
    def store(self):
        posted_data = request.json
        username = posted_data.get("username")
        password = posted_data.get("password")
        sentence = posted_data.get("sentence")

        # verify math of password
        correct_password = self.verify_password(username, password)
        if not correct_password:
            return self.status_generate(302)

        number_tokens = self.count_tokens(username)
        if number_tokens <= 0:
            return self.status_generate(301)

        # verify user has enough tokens
        users.update({"username": username},
                     {
                         "$set": {
                             "sentence": sentence,
                             "tokens": (number_tokens - 1)
                         }})

        return self.status_generate(200, "store save successfully!!")


if __name__ == '__main__':
    app = Bottle()
    # app.install(DemoResource())
    app.install(Register())
    app.install(Store())
    app.run(host="0.0.0.0", port=8080, debug=True, reload=True)
