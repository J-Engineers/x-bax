import random

import validators
from flasgger import swag_from
from flask import Blueprint
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token
from twilio.rest import Client
from werkzeug.security import generate_password_hash, check_password_hash

from src.basics import *
from src.constants.defaults import *
from src.constants.http_status_code import HTTP_400_BAD_REQUEST, HTTP_202_ACCEPTED, HTTP_409_CONFLICT, \
    HTTP_403_FORBIDDEN, HTTP_200_OK, HTTP_201_CREATED
from src.constants.validation import registration_validation, registration_verification_validation, \
    registration_verification_phone_validation, profile_bio_validation, login_validation, reset_validation, \
    public_id_validation
from src.database import db

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth.route('/user/registration', methods=['POST'])
@swag_from('./docs/auth/register.yaml')
def create_user():
    user_email = request.json.get('user_email')
    user_name = request.json.get('user_name')
    user_password = request.json.get('user_password')

    # validate all input
    valid_data = {
        'email': user_email,
        'password': user_password,
        'username': user_name,
    }
    if not registration_validation(valid_data):
        return jsonify({
            "message": "user_email field is required and must be a valid email, "
                       "user_name field is required and must be alphanumeric and up to 3 characters,"
                       "Your user_password field is required and should contain up to 8 characters"
        }), HTTP_400_BAD_REQUEST

    # validate email
    if not validators.email(user_email):
        return jsonify({"message": "Your user_email is invalid"}), HTTP_400_BAD_REQUEST

    new_user = Users.query.filter_by(email=user_email).first()
    if new_user:
        return jsonify({'message': 'User with this email or username already exist'}), HTTP_409_CONFLICT

    new_user = Users.query.filter_by(username=user_name).first()
    if new_user:
        return jsonify(
            {'message': 'User with this username already exist, choose a different username'}), HTTP_409_CONFLICT

    if not create_password(user_password):
        return jsonify({"message": "Your password should contain at least a capital letter and a small latter, "
                                   "  and a number and any of these special characters "
                                   " (+ or @ or  # or $ or % or ^  or = or &)"}), HTTP_400_BAD_REQUEST

    hashed_password = generate_password_hash(user_password, method='sha256')
    public_id = str(uuid.uuid4())
    new_user = Users(
        public_id=public_id,
        is_admin=False,
        user_type=0,
        email=user_email,
        password=hashed_password,
        username=user_name,
        phone=None,
        state_name=None,
        local_government_name=None,
        profile_photo=None,
        name=None,
        updated_on=datetime.datetime.utcnow()
    )
    db.session.add(new_user)
    db.session.commit()

    new_access_token = create_access_token(identity=public_id)
    new_refresh_token = create_refresh_token(identity=public_id)

    new_token_query = Tokens(
        user_id=public_id,
        token=new_access_token,
        blacklisted=False,
        user_reg_stage=1,
        password_recovery=None,
        email_token=None,
        phone_token=None,
        updated_on=datetime.datetime.utcnow()
    )
    db.session.add(new_token_query)
    db.session.commit()

    new_user_1 = Users.query.filter_by(public_id=public_id).first()
    if not new_user_1:
        return jsonify({'message': 'New User  Not Created'}), HTTP_400_BAD_REQUEST

    user_data = {
        "email": new_user_1.email,
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "id": public_id,
        "username": new_user_1.username
    }
    return jsonify({"user": user_data,
                    "message": "Registration successful, an email would be sent to you shortly"}), HTTP_201_CREATED


@auth.route('/user/registration/verify/<public_id>', methods=['GET'])
@swag_from('./docs/auth/verify_email_registration.yaml')
def create_user_1(public_id):
    # validate all input
    valid_data = {
        'public_id': public_id,
    }
    if not public_id_validation(valid_data):
        return jsonify({
            "message": "public_id field is required and must be up to 20,"
        }), HTTP_400_BAD_REQUEST

    user = Users.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"message": "No User Found"}), HTTP_404_NOT_FOUND

    token = Tokens.query.filter_by(user_id=public_id).first()
    if not token:
        return jsonify({"message": "No Token Found"}), HTTP_404_NOT_FOUND

    # update the token now
    new_access_token = create_access_token(identity=user.public_id)
    new_refresh_token = create_refresh_token(identity=user.public_id)
    token.token = new_access_token
    db.session.commit()

    if not int(token.user_reg_stage) == 1:
        return jsonify({"message": "Bad request, user may have passed this process"}), HTTP_403_FORBIDDEN

    token_due = Tokens.query.filter_by(user_id=public_id).first()

    return jsonify({
        "message": "The User exist",
        'access_token': token_due.token,
        'refresh_token': new_refresh_token,
        'id': public_id,
        'email': user.email,
        'user_reg_stage': 1
    }), HTTP_201_CREATED


@auth.route('/user/registration/verify', methods=['POST'])
@jwt_required()
@swag_from('./docs/auth/verify_registration.yaml')
@token_required
def create_user_2(current_user):
    public_id = current_user.public_id

    user = Users.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"message": "No User Found"}), HTTP_404_NOT_FOUND

    token = Tokens.query.filter_by(user_id=public_id).first()
    if not token:
        return jsonify({"message": "No Token Found"}), HTTP_403_FORBIDDEN

    if not int(token.user_reg_stage) == 1:
        return jsonify({"message": "Bad request, check your mail box for your verification token"}), HTTP_403_FORBIDDEN

    email_verification_token = request.json.get('user_token')
    phone = request.json.get('user_phone')

    # validate all input
    valid_data = {
        'email_verification_token': email_verification_token,
        'phone': phone
    }
    if not registration_verification_validation(valid_data):
        return jsonify({
            "message": "user_token field is required and must be up to 5 string digits,"
                       "user_phone field is required and must be numbers and + characters and up to 14 digits"
        }), HTTP_400_BAD_REQUEST

    if not create_phone(str(phone)):
        return jsonify({"message": "phone field should have a + character as prefix"}), HTTP_404_NOT_FOUND

    if not str(email_verification_token) == str(token.email_token):
        return jsonify({"message": "Invalid Verification token"}), HTTP_404_NOT_FOUND

    user.phone = phone
    db.session.commit()

    # send sms to phone

    data = random.sample(range(1, 9), 5)
    sms_token = None
    sms_token_database = None
    for df in data:
        if sms_token is None:
            sms_token = str(df)
        else:
            sms_token = sms_token + '-' + str(df)

        if sms_token_database is None:
            sms_token_database = str(df)
        else:
            sms_token_database = sms_token_database + str(df)

    sms_body = "Your " + os.environ.get("APP_NAME") + " verification token is " + sms_token

    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        messaging_service_sid='MG288fa1be4673684ee127cc8e00eda05b',
        body=sms_body,
        to=phone
    )

    token.user_reg_stage = 2
    token.phone_token = sms_token_database
    db.session.commit()
    data = {
        'token': token.token,
        'id': public_id,
        'email': user.email,
        'username': user.username,
        'phone': user.phone,
        'user_reg_stage': 2
    }

    return jsonify({
        "message": "The User email has been verified, an sms was sent to your phone",
        "data": data,
        "sms": message.sid
    }), HTTP_202_ACCEPTED


@auth.route('/user/registration/verify_phone/<public_id>', methods=['GET'])
@swag_from('./docs/auth/verify_phone_registration.yaml')
def create_user_3(public_id):
    # validate all input
    valid_data = {
        'public_id': public_id,
    }
    if not public_id_validation(valid_data):
        return jsonify({
            "message": "public_id field is required and must be up to 20,"
        }), HTTP_400_BAD_REQUEST

    user = Users.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"message": "No User Found"}), HTTP_404_NOT_FOUND

    token = Tokens.query.filter_by(user_id=public_id).first()
    if not token:
        return jsonify({"message": "No Token Found"}), HTTP_404_NOT_FOUND

    # update the token now
    new_access_token = create_access_token(identity=user.public_id)
    new_refresh_token = create_refresh_token(identity=user.public_id)
    token.token = new_access_token
    db.session.commit()

    if not int(token.user_reg_stage) == 2:
        return jsonify({"message": "Bad request, user may have passed this process"}), HTTP_403_FORBIDDEN

    token_due = Tokens.query.filter_by(user_id=public_id).first()

    return jsonify({
        "message": "The User exist",
        'access_token': token_due.token,
        'refresh_token': new_refresh_token,
        'id': public_id,
        'email': user.email,
        'user_reg_stage': 2
    }), HTTP_201_CREATED


@auth.route('/user/registration/verify', methods=['PUT'])
@jwt_required()
@swag_from('./docs/auth/verify_registration_success.yaml')
@token_required
def create_user_4(current_user):
    public_id = current_user.public_id

    user = Users.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"message": "No User Found"}), HTTP_404_NOT_FOUND

    token = Tokens.query.filter_by(user_id=public_id).first()
    if not token:
        return jsonify({"message": "No Token Found"}), HTTP_404_NOT_FOUND

    if not int(token.user_reg_stage) == 2:
        return jsonify({"message": "Bad request, user may have passed this process"}), HTTP_403_FORBIDDEN

    phone_verification_token = request.json.get('user_token')

    # validate all input
    valid_data = {
        'phone_verification_token': phone_verification_token
    }
    if not registration_verification_phone_validation(valid_data):
        return jsonify({
            "message": "user_token field is required and must be up to 5 string digits,"
        }), HTTP_400_BAD_REQUEST

    if not str(phone_verification_token) == str(token.phone_token):
        return jsonify({"message": "Invalid Verification token"}), HTTP_404_NOT_FOUND

    token.user_reg_stage = 3
    db.session.commit()

    data = {
        'token': token.token,
        'id': public_id,
        'email': user.email,
        'username': user.username,
        'phone': user.phone,
        'user_reg_stage': 3
    }

    return jsonify({
        "message": "The User registration successful",
        "data": data
    }), HTTP_202_ACCEPTED


@auth.route('/user/bio/update', methods=['PUT'])
@jwt_required()
@swag_from('./docs/auth/bio_update.yaml')
@token_required
def update_user(current_user):
    public_id = current_user.public_id
    if not current_user:
        return jsonify({'message': 'Cannot perform that function'}), HTTP_401_UNAUTHORIZED

    state_name = request.json.get('user_state_name')
    local_government_name = request.json.get('user_local_government_name')
    name = request.json.get('user_name')

    # validate all input
    valid_data = {
        'name': name,
        'local_government_name': local_government_name,
        'state_name': state_name,
    }
    if not profile_bio_validation(valid_data):
        return jsonify({
            "message": "user_name field is required and must be up to 8 string digits, "
                       "user_local_government_name field is required and must be up to 4 string digits, "
                       "user_state_name field is required and must be up to 4 string digits,"
        }), HTTP_400_BAD_REQUEST

    user = Users.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"message": "No User Found"}), HTTP_404_NOT_FOUND

    token = Tokens.query.filter_by(user_id=public_id).first()
    if not int(token.user_reg_stage) == 3:
        return jsonify({"message": "Registration process is not complete"}), HTTP_403_FORBIDDEN

    user.name = name
    user.state_name = state_name
    user.local_government_name = local_government_name
    user.updated_on = datetime.datetime.utcnow()
    db.session.commit()

    data = {
        'token': token.token,
        'id': public_id,
        'email': user.email,
        'username': user.username,
        'phone': user.phone,
        'name': user.name,
        'state_name': user.state_name,
        'local_government_name': user.local_government_name,
        'user_reg_stage': 3
    }

    return jsonify({
        "message": "Profile update successful",
        'data': data
    }), HTTP_202_ACCEPTED


@auth.route('/login', methods=['POST'])
@swag_from('./docs/auth/login.yaml')
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    # validate all input
    valid_data = {
        'email': email,
        'password': password,
    }
    if not login_validation(valid_data):
        return jsonify({
            "message": "username field is required and must be a valid email, "
                       "password field is required and must be up to 8 characters"
        }), HTTP_400_BAD_REQUEST

    user = Users.query.filter_by(email=email).first()
    if not user:
        return jsonify(
            {'message': 'User was not found'}
        ), HTTP_400_BAD_REQUEST

    if not check_password_hash(user.password, password):
        return jsonify(
            {'message': 'User password is not correct'}
        ), HTTP_401_UNAUTHORIZED

    new_access_token = create_access_token(identity=user.public_id)
    new_refresh_token = create_refresh_token(identity=user.public_id)

    user_token = Tokens.query.filter_by(user_id=user.public_id).first()
    if not user_token:
        return jsonify(
            {'message': 'Registration required'}
        ), HTTP_400_BAD_REQUEST

    if not int(user_token.user_reg_stage) == 3:
        return jsonify(
            {'message': 'registration verification required'}
        ), HTTP_400_BAD_REQUEST

    password_recovery = user_token.password_recovery
    email_token = user_token.email_token
    phone_token = user_token.phone_token

    db.session.delete(user_token)
    db.session.commit()
    new_token_query = Tokens(
        user_id=user.public_id,
        token=new_access_token,
        blacklisted=False,
        password_recovery=password_recovery,
        email_token=email_token,
        phone_token=phone_token,
        user_reg_stage=3,
        updated_on=datetime.datetime.utcnow()
    )
    db.session.add(new_token_query)
    db.session.commit()

    return jsonify({
        'access_token': new_access_token,
        'refresh_token': new_refresh_token,
        'user_reg_stage': new_token_query.user_reg_stage,
        "data": {
            'username': user.username,
            'name': user.name,
            'state_name': user.state_name,
            'local_government_name': user.local_government_name,
            'id': user.public_id,
            'email': user.email,
            'password': user.password,
            'profile_photo': user.profile_photo,
            'user_type': user.user_type,
            'phone': user.phone,
            'is_admin': user.is_admin,
            'created_on': user.created_on,
            'updated_on': user.updated_on
        }
    }), HTTP_200_OK


@auth.route('/user/password/forget', methods=['PUT'])
@jwt_required()
@swag_from('./docs/auth/submit_password_changes.yaml')
@token_required
def update_user_password(current_user):
    if not current_user:
        return jsonify({'message': 'Cannot perform that function'}), HTTP_401_UNAUTHORIZED

    public_id = current_user.public_id
    email = current_user.email

    user_email = request.json.get('user_email')
    user_token = request.json.get('user_token')
    user_password = request.json.get('user_new_password')
    # validate all input
    valid_data = {
        'email': user_email,
        'password': user_password,
        'email_verification_token': user_token,
    }
    if not reset_validation(valid_data):
        return jsonify({
            "message": "user_email field is required and must be a valid email, "
                       "user_new_password field is required and must be up to 8 characters"
                       "user_token field is required and must be up to 5 string digits,"
        }), HTTP_400_BAD_REQUEST

    token = Tokens.query.filter_by(user_id=public_id).first()
    if not token:
        return jsonify({
            'message': 'User Token not found'
        }), HTTP_404_NOT_FOUND

    if not str(token.password_recovery) == str(user_token):
        return jsonify({
            'message': 'User Token not found in the server'
        }), HTTP_404_NOT_FOUND

    if not int(token.user_reg_stage) == 3:
        return jsonify(
            {'message': 'registration verification required'}
        ), HTTP_400_BAD_REQUEST

    if not create_password(user_password):
        return jsonify(
            {"message": "Your new_password field should contain at least a capital letter and a small latter, "
                        "  and a number and any of these special characters "
                        " (+ or @ or  # or $ or % or ^  or = or &)"}), HTTP_400_BAD_REQUEST

    hashed_password = generate_password_hash(user_password, method='sha256')

    if not email == user_email:
        return jsonify({
            'message': 'User Data mis matched'
        }), HTTP_400_BAD_REQUEST

    current_user.password = hashed_password
    token.user_reg_stage = 3
    token.password_recovery = None
    db.session.commit()

    data = {
        'token': token.token,
        'id': current_user.public_id,
        'email': current_user.email,
        'username': current_user.username,
        'phone': current_user.phone,
        'name': current_user.name,
        'state_name': current_user.state_name,
        'local_government_name': current_user.local_government_name,
        'user_reg_stage': 3
    }

    return jsonify({
        "message": "Password Updated Successfully",
        'data': data
    }), HTTP_202_ACCEPTED


@auth.route('/user/role', methods=['GET'])
@jwt_required()
@swag_from('./docs/auth/user_role.yaml')
@token_required
def get_role_user(current_user):
    if not current_user:
        return jsonify({'message': 'Cannot perform that function'}), HTTP_401_UNAUTHORIZED

    role = int(current_user.user_type)
    data = USER_ROLE['role_' + str(role)][0]
    return jsonify({"data": data}), HTTP_202_ACCEPTED
