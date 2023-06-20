from typing import Dict
from typing import Union

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from lib.core.auth_bearer import handler
from rest_server.user.api_schema import User

# Create FastAPI router
router = APIRouter()


@router.get(path="/user", response_model=User, tags=["User"])
async def get_user(
    request: Request,
    user=handler,
) -> Union[Dict, HTTPException]:
    """
    Get User data API
    """
    cache_store = request.app.cache_store
    logger = request.app.logger
    await logger.info("Get user API")

    # Read user_id from auth data
    user_id = user.get("sub", None)
    if not user_id:
        raise HTTPException(status_code=401)

    response = User()

    # Check if the user exists
    user_address = request.app.address_mapping.get(user_id)

    if not user_address:
        return response

    # fetch user data if user exists
    data_key = f"user_data_{user_address}"
    user_data = cache_store.get_dictionary(data_key)
    response.user_id = user_address
    response.manager_name = user_data.get("manager_name")
    response.team_name = user_data.get("team_name")
    response.signup_complete = True

    return response
