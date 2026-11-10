import bcrypt

def generate_password_hash(password: str) -> str:
    """
    Generates a secure, cryptographically strong salt and hashes the raw password.
    Returns a string ready to be stored in the security.users.password_hash column.
    """
    # Enforce string to bytes conversion for bcrypt compliance
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12) # International performance/security standard balance
    
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against the secured database hash.
    Returns True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
