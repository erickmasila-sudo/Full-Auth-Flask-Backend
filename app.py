"""
API entry point.

Auth endpoints (session-based, cookie stores user_id):
    POST   /signup          create an account and log the user in
    POST   /login            log in an existing user
    DELETE /logout           log out (clears session)
    GET    /check_session    return the current logged-in user, if any

Resource endpoints (all require an active session):
    GET    /notes             list the current user's notes
    POST   /notes              create a note owned by the current user
    GET    /notes/<id>        fetch one of the current user's notes
    PATCH  /notes/<id>        update one of the current user's notes
    DELETE /notes/<id>        delete one of the current user's notes
"""
from functools import wraps

from flask import request, session
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Note
from schemas import SignupSchema, LoginSchema, NoteCreateSchema, NoteUpdateSchema


def login_required(fn):
    """Reject the request with 401 unless a valid session user is present."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id or not db.session.get(User, user_id):
            return {"error": "Unauthorized. Please log in."}, 401
        return fn(*args, **kwargs)

    return wrapper


class Signup(Resource):
    def post(self):
        data = request.get_json() or {}
        try:
            validated = SignupSchema().load(data)
        except ValidationError as err:
            return {"errors": err.messages}, 422

        try:
            user = User(username=validated["username"])
            user.password_hash = validated["password"]
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"error": "Username is already taken"}, 422
        except ValueError as err:
            db.session.rollback()
            return {"error": str(err)}, 422

        session["user_id"] = user.id
        return user.to_dict(), 201


class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        try:
            validated = LoginSchema().load(data)
        except ValidationError as err:
            return {"errors": err.messages}, 422

        user = User.query.filter_by(username=validated["username"]).first()
        if user and user.authenticate(validated["password"]):
            session["user_id"] = user.id
            return user.to_dict(), 200

        return {"error": "Invalid username or password"}, 401


class Logout(Resource):
    def delete(self):
        session.pop("user_id", None)
        return {}, 204


class CheckSession(Resource):
    def get(self):
        user = db.session.get(User, session.get("user_id"))
        if user:
            return user.to_dict(), 200
        return {"error": "No active session"}, 401


class Notes(Resource):
    @login_required
    def get(self):
        notes = Note.query.filter_by(user_id=session["user_id"]).order_by(Note.created_at.desc()).all()
        return [note.to_dict() for note in notes], 200

    @login_required
    def post(self):
        data = request.get_json() or {}
        try:
            validated = NoteCreateSchema().load(data)
        except ValidationError as err:
            return {"errors": err.messages}, 422

        try:
            note = Note(
                title=validated["title"],
                content=validated["content"],
                user_id=session["user_id"],
            )
            db.session.add(note)
            db.session.commit()
        except ValueError as err:
            db.session.rollback()
            return {"error": str(err)}, 422

        return note.to_dict(), 201


class NoteByID(Resource):
    def _get_owned_note(self, id):
        note = db.session.get(Note, id)
        if not note or note.user_id != session["user_id"]:
            return None
        return note

    @login_required
    def get(self, id):
        note = self._get_owned_note(id)
        if not note:
            return {"error": "Note not found"}, 404
        return note.to_dict(), 200

    @login_required
    def patch(self, id):
        note = self._get_owned_note(id)
        if not note:
            return {"error": "Note not found"}, 404

        data = request.get_json() or {}
        try:
            validated = NoteUpdateSchema().load(data, partial=True)
        except ValidationError as err:
            return {"errors": err.messages}, 422

        try:
            for key, value in validated.items():
                setattr(note, key, value)
            db.session.commit()
        except ValueError as err:
            db.session.rollback()
            return {"error": str(err)}, 422

        return note.to_dict(), 200

    @login_required
    def delete(self, id):
        note = self._get_owned_note(id)
        if not note:
            return {"error": "Note not found"}, 404

        db.session.delete(note)
        db.session.commit()
        return {}, 204


api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(CheckSession, "/check_session")
api.add_resource(Notes, "/notes")
api.add_resource(NoteByID, "/notes/<int:id>")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
