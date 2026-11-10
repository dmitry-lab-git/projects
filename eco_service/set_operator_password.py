import asyncio
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
import asyncpg
from security_utils import generate_password_hash

# 1. Declarative configuration loading using Pydantic Settings v2
class DbSettings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "auroville_eco_service"
    db_user: str = "eco_service_app"
    db_password: str
    db_search_path: str = "infrastructure,dicts,security,public"

    # Strict configuration path link targeting the secure folder inside WSL
    model_config = SettingsConfigDict(
        env_file="/home/fujitsu-u745/Projects/secure_folder/eco_service/.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

async def set_user_password(user_id_str: str, plain_password: str):
    """
    Secures and updates the password for a specific user identity inside security.users.
    """
    settings = DbSettings()
    
    # Generate secure bcrypt hash
    secured_hash = generate_password_hash(plain_password)
    
    # Establish asyncpg connection string context
    dsn = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    
    try:
        conn = await asyncpg.connect(dsn)
        
        # Enforce search path session parameters immediately after handshake
        await conn.execute(f"SET search_path TO {settings.db_search_path};")
        
        print(f"🔒 Encrypting credentials for User ID: {user_id_str}...")
        
        # Execute the strict state mutation statement
        result = await conn.execute(
            """
            UPDATE security.users 
            SET password_hash = $1, updated_at = timezone('utc', now())
            WHERE user_id = $2::uuid;
            """,
            secured_hash, user_id_str
        )
        
        if result == "UPDATE 1":
            print(f"✅ Secure password successfully written to security.users ledger context.")
        else:
            print(f"❌ Operation failed: User ID {user_id_str} not found inside security schema.")
            
        await conn.close()
        
    except Exception as e:
        print(f" Critical database layer authentication failure: {e}")

if __name__ == "__main__":
    # Target: Setting a secure web password for CEO Kali Borg
    # Using the exact UUID from our locked database seed script
    KALI_BORG_UUID = "e184fa5b-432d-45ef-bb9e-daefbc23f110"
    
    # In production, this plain password should be passed securely via sys.argv or secure CLI prompts
    TARGET_PASSWORD = "AurovilleSuperSecure2026!" 
    
    asyncio.run(set_user_password(KALI_BORG_UUID, TARGET_PASSWORD))
