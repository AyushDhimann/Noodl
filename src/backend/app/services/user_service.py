from app import logger
from . import supabase_service

def upsert_user_with_checkpoint(wallet_address, name=None, country=None):
    """
    Creates a user or updates them only if name or country are missing.
    This prevents overwriting existing data with nulls.
    """
    wallet_address = wallet_address.lower()
    logger.info(f"SERVICE: Upserting user {wallet_address} with checkpoint.")

    user_res = supabase_service.get_user_by_wallet_full(wallet_address)

    update_data = {}
                                                                             
    if user_res and user_res.data:
                                                               
        existing_user = user_res.data
        logger.info(f"User exists: {existing_user}")

        if not existing_user.get('name') and name:
            update_data['name'] = name
            logger.info(f"Updating missing name for {wallet_address}.")

        if not existing_user.get('country') and country:
            update_data['country'] = country
            logger.info(f"Updating missing country for {wallet_address}.")

        if not update_data:
                                                                      
            logger.info(f"No new info to update for {wallet_address}.")
            return user_res
    else:
                                                                                                       
        logger.info(f"User {wallet_address} not found or API error. Preparing to create new record.")
        update_data = {
            'wallet_address': wallet_address,
            'name': name,
            'country': country
        }

    if update_data:
        return supabase_service.upsert_user(
            wallet_address,
            update_data.get('name'),
            update_data.get('country')
        )

    return user_res
