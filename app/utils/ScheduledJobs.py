from app.database import SessionLocal
from app.models.RefreshModel import RefreshToken
from datetime import datetime, timedelta, timezone

async def delete_old_refresh ():
    db = SessionLocal()

    try: 
        oldToken = db.query(RefreshToken).filter(RefreshToken.expiresAt < datetime.now(timezone.utc) - timedelta(days = 1)).delete()

        db.commit()

    except Exception:
        db.rollback()

    finally:
        db.close()


    




    

