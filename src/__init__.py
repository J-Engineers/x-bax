# This is a flask project
import random

import boto3
from flasgger import Swagger, swag_from
from flask import Flask
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail, Message

from src.admin import admin
from src.auth import auth, decode_auth_token
from src.basics import *
from src.config.swagger import template, swagger_config
from src.constants.defaults import *
from src.constants.http_status_code import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_401_UNAUTHORIZED, \
    HTTP_202_ACCEPTED, HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_408_REQUEST_TIMEOUT
from src.constants.validation import email_validation
from src.database import db, Tokens, Users, Logout
from flask_cors import CORS

s3 = boto3.client('s3',
                  aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                  aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
                  )
BUCKET_NAME = os.environ.get('AWS_BUCKET')
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(BUCKET_NAME)

app_cors_config = {
    "origins": [
        '*',
        'http://localhost:5000',
        'http://e-services-app.herokuapp.com',
        'http://localhost:80',
        'http://localhost:443',
        'http://efficientschools.org.ng'
    ],
    "Access-Control-Allow-Origin": [
        '*',
        'http://localhost:5000',
        'http://e-services-app.herokuapp.com',
        'http://localhost:80',
        'http://localhost:443',
        'http://efficientschools.org.ng'
    ],
    "methods": ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
    "allow_headers": ['Authorization', 'Content-Type', 'accept', 'api_key'],
    "Access-Control-Allow-Headers": [
        'Authorization',
        'Content-Type',
        'accept',
        'api_key'
    ],
}


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            USER_TYPES=USER_TYPES,
            USER_TYPES_DETAILS=USER_TYPES_DETAILS,
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DATABASE_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            MAIL_SERVER=os.environ.get("MAIL_SERVER"),
            MAIL_PORT=int(os.environ.get("MAIL_PORT")),
            MAIL_USERNAME=os.environ.get("MAIL_USERNAME"),
            MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD"),
            MAIL_USE_SSL=bool(os.environ.get("MAIL_USE_SSL")),
            UPLOAD_FOLDER=os.environ.get("UPLOAD_FOLDER"),
            MAX_CONTENT_LENGHT=16 * 1024 * 1024,
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY'),

            SWAGGER={
                'title': "E-Services API",
                'uiversion': 3
            }
        )
    else:
        app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)
    mail = Mail(app)
    JWTManager(app)

    CORS(app, resources={
        r"/api/v1/*": app_cors_config
    })

    @app.route('/api/v1/auth/user/registration/mail', methods=['GET'])
    @jwt_required()
    @swag_from('./docs/register_email.yaml')
    @token_required
    def send_email(current_user):
        email = current_user.email

        data = random.sample(range(1, 9), 5)
        token = None
        token_database = None
        for df in data:
            if token is None:
                token = str(df)
            else:
                token = token + '-' + str(df)

            if token_database is None:
                token_database = str(df)
            else:
                token_database = token_database + str(df)

        # link = os.environ.get("APP_LINK") + "auth/user/registration/verify/" + current_user.public_id
        link = os.environ.get("APP_WEBSITE") + "/user/registration/verify/" + current_user.public_id
        msg = Message(os.environ.get("APP_NAME") + ": Successful Registration", sender=os.environ.get("MAIL_USERNAME"),
                      recipients=email.split())
        msg.html = format_registration_email(link, token)
        token = Tokens.query.filter_by(user_id=current_user.public_id).first()
        if token:
            if int(token.user_reg_stage) == 1:
                token.email_token = token_database
                db.session.commit()
                try:
                    mail.send(msg)
                    return jsonify({
                        "message": 'An E-mail was sent to the user',
                        "token": token.token,
                        "id": token.user_id
                    }), HTTP_201_CREATED
                except:
                    return jsonify({"error": 'Email was not sent, retry: '}), HTTP_408_REQUEST_TIMEOUT
            else:
                return jsonify({"error": 'User has passed this stage of membership settings'}), HTTP_404_NOT_FOUND
        else:
            return jsonify({"error": 'Bad request, invalid token'}), HTTP_403_FORBIDDEN

    @app.route('/api/v1/auth/user/password/forget', methods=['POST'])
    @jwt_required()
    @swag_from('./docs/user_password_email.yaml')
    @token_required
    def send_email_password_recovery_user(current_user):
        email = current_user.email

        user_email = request.json.get('user_email')
        # validate all input
        valid_data = {
            'email': user_email
        }
        if not email_validation(valid_data):
            return jsonify({
                "message": "user_email field is required and must be a valid email address"
            }), HTTP_400_BAD_REQUEST

        if not user_email == email:
            return jsonify({
                'message': 'Mis matched email address'
            }), HTTP_401_UNAUTHORIZED

        data = random.sample(range(1, 9), 5)
        token = None
        token_database = None
        for df in data:
            if token is None:
                token = str(df)
            else:
                token = token + '-' + str(df)

            if token_database is None:
                token_database = str(df)
            else:
                token_database = token_database + str(df)

        # link = os.environ.get("APP_LINK") + "auth/user/password/recovery/" + current_user.public_id
        link = os.environ.get("APP_WEBSITE") + "/user/password/recovery/" + current_user.public_id
        msg = Message(os.environ.get("APP_NAME") + ": Password Recovery", sender=os.environ.get("MAIL_USERNAME"),
                      recipients=email.split())
        msg.html = format_password_forgot_email(link, token)

        token = Tokens.query.filter_by(user_id=current_user.public_id).first()
        if token:
            token.password_recovery = token_database
            db.session.commit()
            try:
                mail.send(msg)
                return jsonify({
                    "message": 'An E-mail was sent to the user',
                    "token": token.token,
                    "id": token.user_id
                }), HTTP_201_CREATED
            except:
                return jsonify({"error": 'Email was not sent, retry: '}), HTTP_408_REQUEST_TIMEOUT
        else:
            return jsonify({"error": 'Bad request, invalid token'}), HTTP_404_NOT_FOUND

    @app.route('/api/v1/auth/password/forget', methods=['POST'])
    @swag_from('./docs/password_email.yaml')
    def send_email_password_recovery_guest():

        user_email = request.json.get('user_email')
        # validate all input
        valid_data = {
            'email': user_email
        }
        if not email_validation(valid_data):
            return jsonify({
                "message": "user_email field is required and must be a valid email address"
            }), HTTP_400_BAD_REQUEST

        user = Users.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({
                'message': 'User not found'
            }), HTTP_404_NOT_FOUND

        data = random.sample(range(1, 9), 5)
        token = None
        token_database = None
        for df in data:
            if token is None:
                token = str(df)
            else:
                token = token + '-' + str(df)

            if token_database is None:
                token_database = str(df)
            else:
                token_database = token_database + str(df)

        # link = os.environ.get("APP_LINK") + "auth/user/password/recovery/" + current_user.public_id
        link = os.environ.get("APP_WEBSITE") + "/user/password/recovery/" + user.public_id
        msg = Message(os.environ.get("APP_NAME") + ": Password Recovery", sender=os.environ.get("MAIL_USERNAME"),
                      recipients=user.email.split())
        msg.html = format_password_forgot_email(link, token)

        token = Tokens.query.filter_by(user_id=user.public_id).first()
        if token:
            token.password_recovery = token_database
            db.session.commit()
            try:
                mail.send(msg)
                return jsonify({
                    "message": 'An E-mail was sent to the user',
                    "token": token.token,
                    "id": token.user_id
                }), HTTP_201_CREATED
            except:
                return jsonify({"error": 'Email was not sent, retry: '}), HTTP_408_REQUEST_TIMEOUT
        else:
            return jsonify({"error": 'Bad request, invalid token'}), HTTP_404_NOT_FOUND

    @app.route('/api/v1/auth/user/password/forget', methods=['GET'])
    @jwt_required()
    @swag_from('./docs/password_reset_email.yaml')
    @token_required
    def send_email_reset_password(current_user):
        email = current_user.email

        data = random.sample(range(1, 9), 5)
        token = None
        token_database = None
        for df in data:
            if token is None:
                token = str(df)
            else:
                token = token + '-' + str(df)

            if token_database is None:
                token_database = str(df)
            else:
                token_database = token_database + str(df)

        link = os.environ.get("APP_WEBSITE")
        msg = Message(os.environ.get("APP_NAME") + ": Password Reset Successful",
                      sender=os.environ.get("MAIL_USERNAME"),
                      recipients=email.split())
        msg.html = format_password_reset_email(link)

        token = Tokens.query.filter_by(user_id=current_user.public_id).first()
        if token:
            token.password_recovery = token_database
            db.session.commit()
            try:
                mail.send(msg)
                return jsonify({
                    "message": 'An E-mail was sent to the user',
                    "token": token.token,
                    "id": token.user_id
                }), HTTP_201_CREATED
            except:
                return jsonify({"error": 'Email was not sent, retry: '}), HTTP_408_REQUEST_TIMEOUT
        else:
            return jsonify({"error": 'Bad request, invalid token'}), HTTP_404_NOT_FOUND

    @app.route('/api/v1/auth/user/picture/update', methods=['POST'])
    @jwt_required()
    @swag_from('./docs/update_picture.yaml')
    @token_required
    def update_user_photo(current_user):
        public_id = current_user.public_id
        if not current_user:
            return jsonify({'message': 'Cannot perform that function'}), HTTP_401_UNAUTHORIZED
        if not request.method == "POST":
            return jsonify({
                'message': 'Request is invalid'
            }), HTTP_401_UNAUTHORIZED

        if 'file' not in request.files:
            return jsonify({
                'message': 'file field cannot be none.'
            }), HTTP_401_UNAUTHORIZED

        image = request.files['file']
        if not image:
            return jsonify({
                'message': 'file field cannot be none.'
            }), HTTP_401_UNAUTHORIZED

        if not allowed_file(image.filename):
            return jsonify({
                'message': 'file extension is not valid'
            }), HTTP_401_UNAUTHORIZED

        # filename = secure_filename(image.filename)
        # image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        uploaded_image_path = upload_file_to_s3(image, BUCKET_NAME, S3_LOCATION, s3, "public-read")
        if uploaded_image_path is None:
            return jsonify({
                'message': 'Could not upload photo to the server'
            }), HTTP_401_UNAUTHORIZED

        user = Users.query.filter_by(public_id=public_id).first()
        if not user:
            return jsonify({"message": "No User Found"}), HTTP_404_NOT_FOUND

        token = Tokens.query.filter_by(user_id=public_id).first()
        if not int(token.user_reg_stage) == 3:
            return jsonify(
                {'message': 'registration verification required'}
            ), HTTP_400_BAD_REQUEST

        user.profile_photo = uploaded_image_path
        db.session.commit()

        return jsonify({
            "message": "Profile picture update successful",
            "url": str(uploaded_image_path)
        }), HTTP_202_ACCEPTED

    @app.route('/api/v1/auth/user/token/refresh', methods=['POST'])
    @jwt_required(refresh=True)
    @swag_from('./docs/refresh_token.yaml')
    def refresh_token():
        public_id = get_jwt_identity()
        # check for refresh token in logout
        header_refresh_token = request.headers['Authorization'].replace("Bearer ", '')

        user_logout_token = Logout.query.filter_by(refresh_token=header_refresh_token).first()
        if user_logout_token:
            return jsonify({'message': "logged out, login"}), HTTP_404_NOT_FOUND

        user = Users.query.filter_by(public_id=public_id).first()
        if not user:
            return jsonify({
                'message': 'Request is invalid'
            }), HTTP_401_UNAUTHORIZED

        token = Tokens.query.filter_by(user_id=public_id).first()
        if not token:
            return jsonify({
                'message': 'Request is invalid'
            }), HTTP_401_UNAUTHORIZED

        if token.blacklisted is True:
            return jsonify({
                'message': 'Your formal token was blacklisted'
            }), HTTP_401_UNAUTHORIZED

        new_access_token = create_access_token(identity=public_id)
        token.token = new_access_token
        db.session.commit()

        return jsonify({
            "message": 'A New token was created',
            "token": new_access_token,
            "id": public_id
        }), HTTP_202_ACCEPTED

    # user authentication route
    app.register_blueprint(auth)

    # admin authentication route
    app.register_blueprint(admin)

    Swagger(app, config=swagger_config, template=template)

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({"error": 'Not Found'}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({"error": 'Something went wrong, we are working on it'}), HTTP_500_INTERNAL_SERVER_ERROR

    return app
