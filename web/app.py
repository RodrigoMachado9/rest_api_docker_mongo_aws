from bottle_resource import BottleResource, api, api_get, api_post, api_put, api_patch, api_delete
from bottle import response, request, run, error, get, post
from pymongo import MongoClient
from passlib.hash import bcrypt
from bottle import Bottle
import spacy
import requests, subprocess, json, uuid, datetime



# instance of mongodb
client = MongoClient("mongodb://mongo:27017")
db = client.dockerDB
user_num = db["user_num"]  # instance of collections one
user_num.insert({
    "num_of_users": 0
})

db = client.sentence_database
users = db["users"]  # instance of collections two

db = client.similarity_db
users_similarity = db["users_similarity"]  # instance of collections two

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

    def status_generate(self, status: int, message: str) -> dict:
        return {"status": status,
                "message": message}


class Store(BottleResource):

    def verify_password(self, username: str, password: str) -> bool:
        hashed_password = users.find({
            "username": username
        })[0]["password"]
        is_equal = True if bcrypt.verify(password, hashed_password) else False
        return is_equal

    def count_tokens(self, username: str) -> int:
        tokens = users.find({"username": username})[0]["tokens"]
        return tokens

    def status_generate(self, status: int, message: str = None) -> dict:
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


class Sentence(BottleResource):


    def verify_password(self, username: str, password: str) -> bool:
        hashed_password = users.find({
            "username": username
        })[0]["password"]
        is_equal = True if bcrypt.verify(password, hashed_password) else False
        return is_equal

    def status_generate(self, status: int, message: str = None):
        return {"status": status,
                "message": message}

    def count_tokens(self, username: str) -> int:
        tokens = users.find({"username": username})[0]["tokens"]
        return tokens

    @api_get('/sentence')
    def sentence(self):
        posted_data = request.json
        username = posted_data.get("username")
        password = posted_data.get("password")

        # verify math of password
        correct_password = self.verify_password(username, password)
        if not correct_password:
            return self.status_generate(302)

        number_tokens = self.count_tokens(username)
        if number_tokens <= 0:
            return self.status_generate(301, "the token limit has been exceeded!")

        # verify user has enough tokens
        users.update({"username": username},
                     {
                         "$set": {
                             "tokens": (number_tokens - 1)
                         }})

        sentence = users.find({
            "username": username
        })[0]["sentence"]

        return self.status_generate(200, sentence)


class Similarity(BottleResource):

    # https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.0.0/en_core_web_sm-2.0.0.tar.gz
    def status_generate(self, status: int, message: str) -> dict:
        return {"status": status, "message": message}

    def user_exists(self, username):
        is_user = users_similarity.find({"username": username}).count()
        return False if (is_user == 0) else True

    @api_post('/register_similarity')
    def register_similarity(self):
        posted_data = request.json
        username = posted_data["username"]
        password = posted_data["password"]
        if self.user_exists(username):
            return self.status_generate(301, "invalid username")

        hashed_password = bcrypt.hash(password)
        users_similarity.insert({
            "username": username,
            "password": hashed_password,
            "tokens": 6
        })
        return self.status_generate(200, "you've successfully signed up to the API")

class Detect(BottleResource):

    def status_generate(self, status: int, message: str, similarity: str = None) -> dict:
        return {"status": status, "similarity": similarity, "message": message}

    def user_exists(self, username: str) -> bool:
        is_user = users_similarity.find({"username": username}).count()
        return False if (is_user == 0) else True

    def verify_password(self, username: str, password: str) -> bool:
        is_user = self.user_exists(username)
        if not is_user:
            return False
        # if user exists then -> check password integrity
        hashed_password = users_similarity.find({
            "username": username})[0]["password"]
        is_equal = bcrypt.verify(password, hashed_password)
        if is_equal:
            return True
        return False

    def count_tokens(self, username: str) -> int:
        tokens = users_similarity.find({
            "username": username
        })[0]["tokens"]
        return tokens


    @api_post('/detect')
    def detect(self):
        posted_data = request.json
        username = posted_data["username"]
        password = posted_data["password"]
        text1 = posted_data["text1"]
        text2 = posted_data["text2"]

        is_user = self.user_exists(username)
        if not is_user:
            return self.status_generate(301, "invalid username")

        correct_password = self.verify_password(username, password)

        if not correct_password:
            return self.status_generate(302, "invalid password")

        num_tokens = self.count_tokens(username)

        if num_tokens <= 0:
            return self.status_generate(303,  "you're tokens, please refill ! ")

        # calculate of distance ...
        nlp = spacy.load('en_core_web_sm')
        text1 = nlp(text1)
        text2 = nlp(text2)


        # ratio is a number between 0 and 1 the closer to 1, the more similar text and text2
        ratio = text1.similarity(text2)
        current_tokens = self.count_tokens(username)
        users_similarity.update({"username": username},
                                 {"$set": {
                                     "tokens": current_tokens - 1
                                 }})

        return self.status_generate(200,  "similarity score calculated successfully",  ratio)


class Refill(BottleResource):

    def status_generate(self, status: int, message: str, similarity: str = None) -> dict:
        return {"status": status, "similarity": similarity, "message": message}

    def user_exists(self, username: str) -> bool:
        is_user = users_similarity.find({"username": username}).count()
        return False if (is_user == 0) else True

    def count_tokens(self, username: str) -> int:
        tokens = users_similarity.find({
            "username": username
        })[0]["tokens"]
        return tokens

    @api_post('/refill')
    def refill(self):
        posted_data = request.json

        username = posted_data["username"]
        password = posted_data["admin_password"]
        refill_amount = posted_data["refill"]

        is_user = self.user_exists(username)
        if not is_user:
            return self.status_generate(301, "invalid username!!")

        # todo >>> build collection to manage administrators ..
        correct_password = "helloworld@123"
        is_correct_password =  True if (correct_password == password) else False
        if not is_correct_password:
            return self.status_generate(304, "invalid admin password !!")

        users_similarity.update({
            "username": username
        }, {"$set": {
            "tokens": refill_amount
        }})

        return self.status_generate(200, "refill successfully!!")


class RegisterImageRecognition(BottleResource):

    def status_generate(self, status: int, message: str, recognition: str = None) -> dict:
        return {"status": status, "recognition": recognition, "message": message}

    def user_exists(self, username: str) -> bool:
        is_user = users_recognition.find({"username": username}).count()
        return False if (is_user == 0) else True

    @api_post('/register_image_recognition')
    def post(self):
        posted_data = request.json

        username = posted_data["username"]
        password = posted_data["password"]

        is_user_exists = self.user_exists(username)
        if is_user_exists:
            return self.status_generate(301,  "this user exists in the database !!")

        hashed_pasword = bcrypt.       hash(password)
        users_recognition.insert({"username": username,
                                  "password": hashed_pasword,
                                  "tokens": 5,
                                  "uuid": uuid.uuid4(),
                                  "created_at": datetime.datetime.now()})

        return self.status_generate(200,  "you successfully signed up !!")


class Classify(BottleResource):

    def status_generate(self, status: int, message: str, recognition: str = None) -> dict:
        return {"status": status, "recognition": recognition, "message": message}

    def verify_credentials(self, username: str, password: str):
        res = ""
        error = ""

        return res, error

    @api_post('/classify')
    def post(self):
        posted_data = request.json
        username = posted_data["username"]
        password = posted_data["password"]
        url = posted_data["url"]


        # todo >>>
        res, errors = self.verify_credentials(username, password)
        if errors:
            return res

        number_tokens = users_recognition.find({"username": username})[0]["tokens"]
        if number_tokens <= 0:
            return self.status_generate(303, "not enougth tokens!")

        r = requests.get(url)












if __name__ == '__main__':
    app = Bottle()
    app.install(Register())
    app.install(Sentence())
    app.install(Store())
    app.install(Similarity())
    app.install(Detect())
    app.install(Refill())
    app.install(RegisterImageRecognition())
    app.run(host="0.0.0.0", port=8080, debug=True, reload=True)
