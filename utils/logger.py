import logging

logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]",

)

logger = logging.getLogger(__name__)


