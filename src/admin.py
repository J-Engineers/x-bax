
from flasgger import swag_from
from flask import Blueprint
from flask_jwt_extended import jwt_required

from src.basics import *
from src.constants.defaults import *
from src.constants.http_status_code import HTTP_202_ACCEPTED, HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_403_FORBIDDEN
from src.constants.validation import public_id_validation, placement_validation
from src.database import db

admin = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


@admin.route('/users', methods=['GET'])
@jwt_required()
@swag_from('./docs/admin/get_all_users.yaml')
@token_required
def get_all_users(current_user):
    if not current_user.is_admin:
        return jsonify({'message': 'Cannot perform that function'}), HTTP_401_UNAUTHORIZED

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    pagination = Users.query.paginate(page=page, per_page=per_page)

    output = []
    output1 = []
    for user in pagination.items:

        user_data = {'name': user.name, 'username': user.username, 'email': user.email, 'id': user.public_id,
                 'password': user.password, 'is_admin': user.is_admin, 'user_role': get_user_role(user.user_type),
                 'phone': user.phone, 'created_on': user.created_on, 'user_reg_stage': token.user_reg_stage,
                 'state_name': user.state_name, 'local_government_name': user.local_government_name,
                 'profile_photo': user.profile_photo}

        token = Tokens.query.filter_by(user_id=user.public_id).first()
        if not token or int(token.user_reg_stage) < 3:
            output1.append(user_data)
        output.append(user_data)

    meta = {
        "page": pagination.page,
        "pages": pagination.pages,
        "total_count": pagination.total,
        "prev_page": pagination.prev_num,
        "next_page": pagination.next_num,
        "has_prev": pagination.has_prev,
        "has_next": pagination.has_next
    }

    return jsonify(
        {
            "complete_registration": output,
            "not_complete_registration": output1,
            "meta": meta
        }
    ), HTTP_200_OK


@admin.route('/user/<public_id>', methods=['GET'])
@jwt_required()
@swag_from('./docs/admin/get_one_users.yaml')
@token_required
def get_one_user(current_user, public_id):
    # validate all input
    valid_data = {
        'public_id': public_id
    }
    if not public_id_validation(valid_data):
        return jsonify({
            "message": "public_id field is required and must be up to 20,"
        }), HTTP_400_BAD_REQUEST

    if not current_user.is_admin:
        return jsonify({'message': 'Cannot perform that function'}), HTTP_401_UNAUTHORIZED

    user = Users.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"message": "No User Found"}), HTTP_404_NOT_FOUND

    token = Tokens.query.filter_by(user_id=user.public_id).first()
    if not token:
        return jsonify({"message": "No User Found"}), HTTP_404_NOT_FOUND

    user_data = {'name': user.name, 'username': user.username, 'email': user.email, 'id': user.public_id,
                 'password': user.password, 'is_admin': user.is_admin, 'user_role': get_user_role(user.user_type),
                 'phone': user.phone, 'created_on': user.created_on, 'user_reg_stage': token.user_reg_stage,
                 'state_name': user.state_name, 'local_government_name': user.local_government_name,
                 'profile_photo': user.profile_photo}

    return jsonify({"user": user_data}), HTTP_200_OK


@admin.route('/user/placement', methods=['PUT'])
@jwt_required()
@swag_from('./docs/admin/update_user_placement.yaml')
@token_required
def placement(current_user):
    user_types_config = USER_TYPES
    config_type = len(user_types_config) - 1
    public_id = request.json.get('public_id')
    # validate all input
    valid_data = {
        'public_id': public_id
    }
    if not public_id_validation(valid_data):
        return jsonify({
            "message": "public_id field is required and must be up to 20,"
        }), HTTP_400_BAD_REQUEST

    if current_user.public_id == public_id:
        return jsonify({'message': 'Cannot perform that function'}), HTTP_401_UNAUTHORIZED

    if not current_user.is_admin:
        if int(current_user.user_type) < config_type:
            return jsonify({'message': 'Cannot perform that function'}), HTTP_401_UNAUTHORIZED

    token = Tokens.query.filter_by(user_id=public_id).first()
    if not token:
        return jsonify({"message": "No User Found"}), HTTP_404_NOT_FOUND

    if int(token.user_reg_stage) < 3:
        return jsonify({"message": "User registration is not complete"}), HTTP_404_NOT_FOUND

    level = request.json.get('level')
    # validate all input
    valid_data = {
        'placement': level
    }
    if not placement_validation(valid_data):
        return jsonify({
            "message": "level field is required and must be one or two string,"
        }), HTTP_400_BAD_REQUEST

    user_type = int(level)

    if user_type > config_type or user_type < 0:
        return jsonify({"message": USER_TYPES_DETAILS}
                       ), HTTP_400_BAD_REQUEST

    user = Users.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"message": "No User Found"}), HTTP_404_NOT_FOUND

    user.user_type = user_type
    user.updated_on = datetime.datetime.utcnow()
    if user_type == 6 or user_type == 9 or user_type == 10:
        user.is_admin = True
    else:
        user.is_admin = False
    db.session.commit()

    return jsonify({"message": "The User level has been updated to " + user_types_config[user_type]}), HTTP_200_OK


@admin.route('/user/blacklist/<public_id>', methods=['GET'])
@jwt_required()
@swag_from('./docs/admin/update_user_blacklist.yaml')
@token_required
def blacklist_user(current_user, public_id):
    # validate all input
    valid_data = {
        'public_id': public_id
    }
    if not public_id_validation(valid_data):
        return jsonify({
            "message": "public_id field is required and must be up to 20,"
        }), HTTP_400_BAD_REQUEST

    if not current_user.is_admin:
        return jsonify({'message': 'Cannot perform that function'}), HTTP_401_UNAUTHORIZED

    token = Tokens.query.filter_by(user_id=public_id).first()
    if not token:
        return jsonify({"message": "No User Found"}), HTTP_404_NOT_FOUND

    if int(token.user_reg_stage) < 3:
        return jsonify({"message": "User registration is not complete"}), HTTP_404_NOT_FOUND

    token.blacklisted = True
    token.updated_on = datetime.datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "The User Token has been blacklisted"}), HTTP_200_OK


@admin.route('/user/cancel_blacklist/<public_id>', methods=['GET'])
@jwt_required()
@swag_from('./docs/admin/cancel_user_blacklist.yaml')
@token_required
def cancel_blacklist_user(current_user, public_id):
    # validate all input
    valid_data = {
        'public_id': public_id
    }
    if not public_id_validation(valid_data):
        return jsonify({
            "message": "public_id field is required and must be up to 20,"
        }), HTTP_400_BAD_REQUEST

    if not current_user.is_admin:
        return jsonify({'message': 'Cannot perform that function'}), HTTP_401_UNAUTHORIZED

    token = Tokens.query.filter_by(user_id=public_id).first()
    if not token:
        return jsonify({"message": "No User Found"}), HTTP_404_NOT_FOUND

    if int(token.user_reg_stage) < 3:
        return jsonify({"message": "User registration is not complete"}), HTTP_404_NOT_FOUND

    token.blacklisted = False
    token.updated_on = datetime.datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "The User Token  blacklisted was cancelled"}), HTTP_200_OK


@admin.route('/user/<public_id>', methods=['DELETE'])
@jwt_required()
@swag_from('./docs/admin/delete_user.yaml')
@token_required
def delete_user(current_user, public_id):
    # validate all input
    valid_data = {
        'public_id': public_id
    }
    if not public_id_validation(valid_data):
        return jsonify({
            "message": "public_id field is required and must be up to 20,"
        }), HTTP_400_BAD_REQUEST

    if not current_user.is_admin:
        return jsonify({'message': 'Cannot perform that function'}), HTTP_401_UNAUTHORIZED

    if current_user.pubic_id == public_id:
        return jsonify({'message': 'Cannot perform that function'}), HTTP_403_FORBIDDEN

    user = Users.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"message": "No User Found"}), HTTP_404_NOT_FOUND

    token = Tokens.query.filter_by(user_id=public_id).first()
    if not token:
        return jsonify({"message": "No User Found"}), HTTP_404_NOT_FOUND

    if int(token.user_reg_stage) < 3:
        return jsonify({"message": "User registration is not complete"}), HTTP_404_NOT_FOUND

    db.session.delete(token)

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "The User has been deleted"}), HTTP_202_ACCEPTED


@admin.route('/user/roles', methods=['GET'])
@jwt_required()
@swag_from('./docs/admin/get_users_role.yaml')
@token_required
def get_roles(current_user):
    if not current_user.is_admin:
        return jsonify({'message': 'Cannot perform that function'}), HTTP_401_UNAUTHORIZED

    role = int(current_user.user_type)
    start = 0
    data = []
    while start < role:
        start += 1
        data.append(USER_ROLE['role_' + str(start)][0])

    return jsonify({"data": data}), HTTP_202_ACCEPTED


@admin.route('/user/role/<public_id>', methods=['GET'])
@jwt_required()
@swag_from('./docs/admin/get_user_role.yaml')
@token_required
def get_role_admin(current_user, public_id):
    # validate all input
    valid_data = {
        'public_id': public_id
    }
    if not public_id_validation(valid_data):
        return jsonify({
            "message": "public_id field is required and must be up to 20,"
        }), HTTP_400_BAD_REQUEST

    if not current_user.is_admin:
        return jsonify({'message': 'Cannot perform that function'}), HTTP_401_UNAUTHORIZED

    user = Users.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"message": "No User Found"}), HTTP_404_NOT_FOUND

    token = Tokens.query.filter_by(user_id=public_id).first()
    if not token:
        return jsonify({"message": "No User Found"}), HTTP_404_NOT_FOUND

    if int(token.user_reg_stage) < 3:
        return jsonify({"message": "User registration is not complete"}), HTTP_404_NOT_FOUND

    role = int(user.user_type)
    data = USER_ROLE['role_' + str(role)][0]
    return jsonify({"data": data}), HTTP_202_ACCEPTED
