from app.auth.jwt_token import create_access_token,create_refresh_token,decode_token
import pytest

def test_invalid_token_rejected():
    with pytest.raises(Exception):
        decode_token("this_is_not_avilablei")

def test_invalid_token_is_rejected():
    with pytest.raises(Exception):
        decode_token("this-is-not-a-valid-jwt")
def test_create_accesstoken():
    user_id = "abc123"
    token = create_access_token(user_id)
    assert token is not None
    assert  isinstance(token,str)
    assert len(token)>0

def test_refresh_token():
    user_id = "abc123"
    token = create_access_token(user_id)
    assert token is not None
    assert isinstance(token,str)
    assert len(token)>0

def test_access_token_contains_current_user():
    user_id = "abc123"
    token = create_access_token(user_id)
    payload = decode_token(token)
    assert payload["sub"] == user_id
    assert payload["type"]== "access"
def test_refresh_token_contains_current_user():
    user_id = "abc123"
    token = create_refresh_token(user_id)
    payload = decode_token(token)
    assert payload["sub"] == user_id
    assert payload["type"]== "refresh"

def test_access_and_refresh_token_aredifferent():
    user_id = "abc123"
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    assert access_token != refresh_token



def test_invalid_token_is_rejected():
    with pytest.raises(Exception):
        decode_token("this-is-not-a-valid-jwt")