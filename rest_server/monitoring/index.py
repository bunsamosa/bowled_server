from typing import Dict
from typing import Union

from fastapi import APIRouter
from fastapi import HTTPException

from lib.core.auth_bearer import handler

# Create FastAPI router
router = APIRouter()


@router.get(path="/", response_model=Dict, tags=["Monitoring"])
async def index(user=handler) -> Union[Dict, HTTPException]:
    """
    Index API
    """

    return user
