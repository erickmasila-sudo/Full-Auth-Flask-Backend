"""
API entry point.

Auth endpoints (session-based, cookie stores user_id):
    POST   /signup          create an account and log the user in
    POST   /login            log in an existing user
    DELETE /logout           log out (clears session)
    GET    /check_session    return the current logged-in user, if any
"""
from flask import request, session
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Note
from schemas import SignupSchema, LoginSchema


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


api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(CheckSession, "/check_session")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
