from django.core.exceptions import (
    ObjectDoesNotExist,
    MultipleObjectsReturned
)

from .Models.users import User


def get_user_with_name(name):
    try:
        user = User.objects.get(name__iexact=name)
    except (ObjectDoesNotExist, MultipleObjectsReturned) as exception:
        if exception == ObjectDoesNotExist:
            error_msg = u"No user exists with the same name."
        else:
            error_msg = u"There are more than one user with the same name."

    if user:
        return user
    else:
        return error_msg
