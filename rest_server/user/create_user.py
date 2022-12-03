from typing import Dict
from typing import Union

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from hdwallet.hdwallet import HDWallet
from hdwallet.utils import generate_mnemonic
from rest_server.user.api_schema import CreateUser
from rest_server.user.api_schema import User

from lib.core.auth_bearer import handler

# Create FastAPI router
router = APIRouter()


@router.post(path="/user", response_model=User, tags=["User"])
async def create_user(
    request: Request,
    data: CreateUser,
    user=handler,
) -> Union[Dict, HTTPException]:
    """
    Create User API
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
    address_key = f"user_address_{user_id}"
    user_address = cache_store.get_key(address_key)

    # If not create a new user from mnemonic
    if not user_address:
        mnemonic = generate_mnemonic(language="english", strength=128)
        wallet = HDWallet(symbol="ETH").from_mnemonic(mnemonic=mnemonic)
        private_key = wallet.private_key()

        user_address = f"0x{wallet.hash()}"
        cache_store.set_key(key=address_key, value=user_address)

        data_key = f"user_data_{user_address}"
        user_data = cache_store.get_dictionary(data_key)
        user_data["manager_name"] = data.manager_name
        user_data["team_name"] = data.team_name
        user_data["mnemonic"] = mnemonic
        user_data["private_key"] = private_key
    else:
        user_address = str(user_address, encoding="UTF-8")

    # if user already exists, return existing user data
    data_key = f"user_data_{user_address}"
    user_data = cache_store.get_dictionary(data_key)
    response.user_id = user_address
    response.manager_name = user_data.get("manager_name")
    response.team_name = user_data.get("team_name")
    response.signup_complete = True

    return response
