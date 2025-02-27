import os
from datetime import datetime
from http import HTTPStatus

import jwt
from flask import Blueprint, Response, json, request
from flask_bcrypt import Bcrypt

from src.core.models.user import User
from src.factory import bcrypt, db

# user controller blueprint to be registered with api blueprint
users = Blueprint("auth", __name__)


# route for login api/auth/signin
@users.route("/signin", methods=["GET", "POST"])
def handle_login():
    try:
        # first check user parameters
        data = request.json
        if "email" and "password" in data:
            # check db for user records
            user = User.query.filter_by(email=data["email"]).first()

            # if user records exists we will check user password
            if user:
                # check user password
                if bcrypt.check_password_hash(user.password, data["password"]):
                    # user password matched, we will generate token
                    payload = {
                        "iat": datetime.utcnow(),
                        "user_id": str(user.id).replace("-", ""),
                        "email": user.email,
                    }
                    token = jwt.encode(
                        payload, os.getenv("SECRET_KEY"), algorithm="HS256"
                    )
                    return Response(
                        response=json.dumps(
                            {
                                "status": "success",
                                "message": "User Sign In Successful",
                                "token": token,
                            }
                        ),
                        status=HTTPStatus.OK,
                        mimetype="application/json",
                    )

                else:
                    return Response(
                        response=json.dumps(
                            {"status": "failed", "message": "User Password Mistmatched"}
                        ),
                        status=HTTPStatus.UNAUTHORIZED,
                        mimetype="application/json",
                    )
            # if there is no user record
            else:
                return Response(
                    response=json.dumps(
                        {
                            "status": "failed",
                            "message": "User Record doesn't exist, kindly register",
                        }
                    ),
                    status=HTTPStatus.NOT_FOUND,
                    mimetype="application/json",
                )
        else:
            # if request parameters are not correct
            return Response(
                response=json.dumps(
                    {
                        "status": "failed",
                        "message": "User Parameters Email and Password are required",
                    }
                ),
                status=HTTPStatus.BAD_REQUEST,
                mimetype="application/json",
            )

    except Exception as e:
        return Response(
            response=json.dumps(
                {"status": "failed", "message": "Error Occured", "error": str(e)}
            ),
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype="application/json",
        )


# route for login api/auth/signup
@users.route("/signup", methods=["GET", "POST"])
def handle_signup():
    try:
        # first validate required use parameters
        data = request.json
        if data and "email" and "password" in data:
            # validate if the user exist
            user = User.query.filter_by(email=data["email"]).first()
            # usecase if the user doesn't exists
            if not user:
                # creating the user instance of User Model to be stored in DB
                user_obj = User(
                    email=data["email"],
                    # hashing the password
                    password=bcrypt.generate_password_hash(data["password"]).decode(
                        "utf-8"
                    ),
                )
                db.session.add(user_obj)
                db.session.commit()

                # lets generate jwt token
                payload = {
                    "iat": datetime.utcnow(),
                    "user_id": str(user_obj.id).replace("-", ""),
                    "email": user_obj.email,
                }
                token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")
                return Response(
                    response=json.dumps(
                        {
                            "status": "success",
                            "message": "User Sign up Successful",
                            "token": token,
                        }
                    ),
                    status=HTTPStatus.CREATED,
                    mimetype="application/json",
                )
            else:
                print(user)
                # if user already exists
                return Response(
                    response=json.dumps(
                        {
                            "status": "failed",
                            "message": "User already exists kindly use sign in",
                        }
                    ),
                    status=HTTPStatus.CONFLICT,
                    mimetype="application/json",
                )
        else:
            # if request parameters are not correct
            return Response(
                response=json.dumps(
                    {
                        "status": "failed",
                        "message": "User Parameters, Email and Password are required",
                    }
                ),
                status=HTTPStatus.BAD_REQUEST,
                mimetype="application/json",
            )
    except Exception as e:
        return Response(
            response=json.dumps(
                {"status": "failed", "message": "Error Occured", "error": str(e)}
            ),
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype="application/json",
        )
