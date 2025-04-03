import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/exam_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")



#clintid: 440943321152-qsv2evqr3knpoe5gmkvlvr02g483ikvp.apps.googleusercontent.com
#client_secret: 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