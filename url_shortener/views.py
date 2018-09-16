from flask import request, redirect, g
from url_shortener import app
from url_shortener.stores.links_store import LinksStore
from utils.redis_db import get_redis_connection
from utils.responses import error_json_response, success_json_response, parse_and_validate_json_args


def get_cached_links_store():
    if not hasattr(g, 'links_store'):
        g.links_store = LinksStore(
            redis_db=get_redis_connection(
                host='localhost',
                port=6379,
                db=0,
            ),
            number_of_counters=992,
            max_id=62 ** 5,
            max_url_length=1000
        )

    return g.links_store


@app.route("/shorten_url", methods=['POST'])
def shorten_url():
    error_message, kwargs = parse_and_validate_json_args(request, ['url'])
    if error_message:
        return error_json_response(error_message, 400)
    long_url = kwargs['url']

    links_store = get_cached_links_store()
    error_message, short_url = links_store.shorten_url(long_url)
    if error_message:
        return error_json_response(error_message, 400)

    return success_json_response({'shortened_url': request.host_url + short_url}, 201)


@app.route("/<short_url>", methods=['GET'])
def redirect_url(short_url):
    links_store = get_cached_links_store()

    long_url = links_store.lengthen_url(short_url)
    if long_url:
        return redirect(long_url, code=302)
    else:
        return error_json_response("Url '{}' not found.".format(short_url), 404)


@app.errorhandler(Exception)
def handle_unknown_error(e):
    return error_json_response("Unexpected error: {}".format(str(e)), 500)