from flask import Blueprint, request, jsonify
from app import logger
from app.services import supabase_service

bp = Blueprint('search_routes', __name__, url_prefix='/search')


@bp.route('', methods=['GET'])
def search_paths_route():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    if len(query) < 2:
        return jsonify([]) # Return empty list if query is too short

    logger.info(f"ROUTE: /search GET for query: '{query}'")
    try:
        results = supabase_service.hybrid_search_paths(query)
        return jsonify(results)
    except Exception as e:
        logger.error(f"ROUTE: /search GET failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to perform search."}), 500