from .models import User, UserPermission
from werkzeug.security import gen_salt

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_ID = -1

DEFAULT_ADMIN_USER = User.make_user(DEFAULT_ADMIN_USERNAME, gen_salt(64), UserPermission.Admin)
DEFAULT_ADMIN_USER.id = DEFAULT_ADMIN_ID