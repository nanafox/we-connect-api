from typing import Annotated

from fastapi import Depends

from posts_app import oauth2, schemas

CurrentUserDependency = Annotated[
    schemas.User, Depends(oauth2.get_current_user)
]

UserDependency = Depends(oauth2.get_current_user)
