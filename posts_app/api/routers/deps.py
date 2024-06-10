from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from posts_app.database import get_db
from posts_app.utils import get_query_params

QueryParamsDependency = Annotated[dict, Depends(get_query_params)]
DBSessionDependency = Annotated[Session, Depends(get_db)]
