from fastapi import FastAPI


def test_fastapi_app_can_be_instantiated():
    app = FastAPI()
    assert app is not None
