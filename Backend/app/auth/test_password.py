from app.auth.password import hash_password,verify_password

password = "Rishabh125"

hashed =  hash_password(password)
print("Original password ", password)
print("Hashed password ", hashed)

print("Correct Password", verify_password(password,hashed))
print("wrong password", verify_password("wrong",hashed))
