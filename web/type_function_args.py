from beartype import beartype


@beartype
def test(name: str):
    return 'hello %s' % name


def test1(name: str):
    return 'hello %s' % name


# from fastapi import FastAPI
# from uvicorn import run
#
# app = FastAPI()
#
#
# @app.get('/fastapi')
# def hello_world():
#     return {"status": 200, "message": " helloworld"}
#
#
#
# if __name__ == '__main__':
#     run(app)