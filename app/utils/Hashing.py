from passlib.context import CryptContext

secure_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")

def hashPassword (password : str):
    return secure_context.hash(password)

def verifyPassword (plain:str, hashed: str):
    return secure_context.verify(plain, hashed)