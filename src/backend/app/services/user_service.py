from app import logger
from . import supabase_service


def upsert_user_with_checkpoint(wallet_address, name=None, country=None):
    """
    Creates a user or updates them only if name or country are missing.
    This prevents overwriting existing data with nulls.
    """
    logger.info(f"SERVICE: Upserting user {wallet_address} with checkpoint.")

    # First, check if the user exists and get their current data
    user_res = supabase_service.get_user_by_wallet_full(wallet_address)

    update_data = {}
    # FIX: Check if user_res is not None before accessing its data attribute.
    if user_res and user_res.data:
        # User exists, check if we need to fill in missing info
        existing_user = user_res.data
        logger.info(f"User exists: {existing_user}")

        if not existing_user.get('name') and name:
            update_data['name'] = name
            logger.info(f"Updating missing name for {wallet_address}.")

        if not existing_user.get('country') and country:
            update_data['country'] = country
            logger.info(f"Updating missing country for {wallet_address}.")

        if not update_data:
            # No new information to add, just return the existing user
            logger.info(f"No new info to update for {wallet_address}.")
            return user_res
    else:
        # This block now correctly handles both "user not found" and API errors where user_res is None.
        logger.info(f"User {wallet_address} not found or API error. Preparing to create new record.")
        update_data = {
            'wallet_address': wallet_address,
            'name': name,
            'country': country
        }

    # Perform the upsert operation only if there's something to change or insert
    if update_data:
        return supabase_service.upsert_user(
            wallet_address,
            update_data.get('name'),
            update_data.get('country')
        )

    # This case is for when the user exists and no new data was provided
    return user_res