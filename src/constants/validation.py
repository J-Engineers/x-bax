import gladiator as gl

"""
Parameters:

    data: data in consideration
    validators: tells on what basis validation has to be done
        required :  The required validator to check for presence of field always.
        format_email : Validator for checking email.
        length_max : Checks for maximum length of text.
        length_min : Checks for minimum text length.
        length : Checks for particular length.
        type_ : Checks for particular type.
        regex_ : Checks for regex.
        _value : Checks for particular value.
        in_ : Checks in particular list.
        lt : Checks for less than integer value.
        gt : Checks for greater than integer value.
        eq : Checks for equal integer value.
        ne : Checks for not equal integer value.
        gte : Checks for greater than equal integer value.
        lte : Checks for less than equal to integer value.
        true_if_empty : If empty, this validator returns true.
        skip_on_fail : If the validation failed, this can be used to skip testing for validation.
"""


# validate all input
def registration_validation(input_fields):
    field_validations = (
        ('email', gl.required, gl.format_email),
        ('password', gl.required, gl.length_min(8)),
        ('username', gl.required, gl.length_min(3), gl.type_(str), gl.regex_('[a-zA-Z][a-zA-Z ]+')),
    )
    result = gl.validate(field_validations, input_fields)
    return bool(result)


def registration_verification_validation(input_fields):
    field_validations = (
        ('email_verification_token', gl.required, gl.type_(str), gl.length(5, 5)),
        ('phone', gl.required, gl.type_(str), gl.length_min(14), gl.regex_('[0-9+]+')),
    )
    result = gl.validate(field_validations, input_fields)
    return bool(result)


def registration_verification_phone_validation(input_fields):
    field_validations = (
        ('phone_verification_token', gl.required, gl.type_(str), gl.length(5, 5)),
    )
    result = gl.validate(field_validations, input_fields)
    return bool(result)


def profile_bio_validation(input_fields):
    field_validations = (
        ('name', gl.required, gl.type_(str), gl.length_min(8), gl.regex_('[a-zA-Z][a-zA-Z ]+')),
        ('local_government_name', gl.required, gl.type_(str), gl.length_min(4), gl.regex_('[a-zA-Z][a-zA-Z ]+')),
        ('state_name', gl.required, gl.type_(str), gl.length_min(4), gl.regex_('[a-zA-Z][a-zA-Z ]+')),
    )
    result = gl.validate(field_validations, input_fields)
    return bool(result)


def login_validation(input_fields):
    field_validations = (
        ('email', gl.required, gl.format_email),
        ('password', gl.required, gl.length_min(8)),
    )
    result = gl.validate(field_validations, input_fields)
    return bool(result)


def reset_validation(input_fields):
    field_validations = (
        ('email', gl.required, gl.format_email),
        ('password', gl.required, gl.length_min(8)),
        ('email_verification_token', gl.required, gl.type_(str), gl.length(5, 5)),
    )
    result = gl.validate(field_validations, input_fields)
    return bool(result)


def email_validation(input_fields):
    field_validations = (
        ('email', gl.required, gl.format_email),
    )
    result = gl.validate(field_validations, input_fields)
    return bool(result)


def public_id_validation(input_fields):
    field_validations = (
        ('public_id', gl.required, gl.type_(str), gl.length_min(20)),
    )
    result = gl.validate(field_validations, input_fields)
    return bool(result)


def placement_validation(input_fields):
    field_validations = (
        ('placement', gl.required, gl.type_(str), gl.length(1, 2), gl.regex_('[0-9]+')),
    )
    result = gl.validate(field_validations, input_fields)
    return bool(result)
