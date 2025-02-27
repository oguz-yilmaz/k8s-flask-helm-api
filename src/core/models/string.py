from src.factory import db


class String(db.Model):
    __tablename__ = "strings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    value = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
