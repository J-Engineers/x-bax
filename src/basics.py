import uuid
from functools import wraps

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity

from src.constants.http_status_code import HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED
from src.database import Tokens, Users, Logout
from src.constants.defaults import *
import re
import datetime
import os
import jwt


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        public_id = get_jwt_identity()
        if not "Authorization" in request.headers:
            return jsonify({'message': "Credentials are missing"}), HTTP_404_NOT_FOUND

        header_token = request.headers['Authorization'].replace("Bearer ", '')

        current_user = Users.query.filter_by(public_id=public_id).first()
        if not current_user:
            return jsonify({'message': "User not found"}), HTTP_404_NOT_FOUND

        token = Tokens.query.filter_by(user_id=public_id).first()
        if not token:
            return jsonify({'message': "Credentials are missing"}), HTTP_404_NOT_FOUND
        if not token.token == header_token:
            return jsonify({'message': "Credentials Expired"}), HTTP_404_NOT_FOUND
        if token.token == '':
            return jsonify({'message': "logged out, login"}), HTTP_404_NOT_FOUND

        user_type = int(current_user.user_type)
        config_type = len(USER_TYPES)

        if user_type > (config_type - 1) or user_type < 0:
            return jsonify({'message': 'Invalid user type'}), HTTP_404_NOT_FOUND

        return f(current_user, *args, **kwargs)

    return decorated


def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            os.environ.get("SECRET_KEY"),
            algorithm='HS256'
        ).decode('utf-8')
    except Exception as e:
        return e


def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(auth_token, os.environ.get("SECRET_KEY"))
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return None


def create_password(password):
    if not password:
        return False
    new_password = password

    if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', new_password):
        return True
    else:
        return False


def create_phone(phone):
    if not phone:
        return False
    map0 = phone.split("+")
    if len(map0) == 1:
        return False
    else:
        return True


def allowed_file(filename):
    allowed_filenames = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_filenames


def upload_file_to_s3(file, bucket_name, location, s3, acl="public-read"):
    """
    Docs: http://boto3.readthedocs.io/en/latest/guide/s3.html
    """
    try:
        filename_ext = file.filename.split('.')[1]
        filename_name_old = file.filename.split('.')[0]
        c6 = uuid.uuid4()
        filename_name = str(c6) + filename_name_old + "." + filename_ext
        file.filename = filename_name
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type  # Set appropriate content type as per the file
            }
        )
    except Exception as e:
        return None
    return "{}{}".format(location, file.filename)


def format_registration_email(link, token):
    data = "<h3>Welcome to our platform, use the token below:<h3>" \
           "<h3>Visit this link and type in your token below and click continue. </h3>" \
           "<h1>" + token + "</h1>" \
                            "<h3><a style='background-color:blue;color:white;width:300px;height:50px' href=" + link + ">" \
                                                                                                                      "click here</a><h3><h3>Thank you for registering with us</h3><hr><h5>Regards, </h5>" \
                                                                                                                      "<h4>" + os.environ.get(
        "APP_DEVELOPER_NAME") + "</h4><h3>" + os.environ.get("APP_NAME") + "<h3>"
    return data


def format_password_forgot_email(link, token):
    data = "<h3>Use the token below:<h3>" \
           "<h3>Visit this link and type in your token to continue with your change of account password.</h3>" \
           "<h1>" + token + "</h1><h3><a style='background-color:blue;color:white;width:300px;height:50px' " \
                            "href=" + link + ">click here</a><h3> <h3>Thank you for registering with us</h3><hr><h5>Regards, </h5>" \
                                             "<h4>" + os.environ.get(
        "APP_DEVELOPER_NAME") + "</h4><h3>" + os.environ.get("APP_NAME") + "<h3>"
    return data


def format_password_reset_email(link):
    data = "<h3>Welcome to our platform, Your password has be updated successfully:<h3>" \
           "<h3>Go to our website</h3><h3><a style='background-color:blue;color:white;width:300px;height:50px' " \
           "href=" + link + ">click here</a><h3> <h3>Thank you for registering with us</h3><hr><h5>Regards, </h5>" \
                            "<h4>" + os.environ.get("APP_DEVELOPER_NAME") + "</h4><h3>" + os.environ.get(
        "APP_NAME") + "<h3>"
    return data


def get_user_role(role_id):
    return USER_ROLE['role_' + str(role_id)][0]['target']

