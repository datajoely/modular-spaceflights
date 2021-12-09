import logging
import sys
from urllib.request import urlopen

checks = {}
for link in sys.argv[1:]:
    try:
        status = urlopen(link, timeout=5).status
        checks[link] = status
    except:  # noqa: E722
        checks[link] = status


failures = {url: code for url, code in checks.items() if code != 200}

if failures:
    logger = logging.getLogger(__name__)
    for url, code in failures.items():
        logger.error(url, code)
    sys.exit(1)
sys.exit(0)
