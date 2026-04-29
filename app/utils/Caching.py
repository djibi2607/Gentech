from app.models.UserModel import User
from fastapi import Request

def user_key_builder (func, namespace = "", request: Request = None, **kwargs) -> str:
    kwargs_copy = kwargs.get("kwargs", {})
    current_user = kwargs_copy.get("current_user")
    return f"Balance:{current_user.user_id}"