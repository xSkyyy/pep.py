"""Global objects and variables"""

import time
from collection.channels import ChannelList
from collection.matches import MatchList
from collection.streams import StreamList
from collection.tokens import TokenList
from config import conf

# Consts.
DATADOG_PREFIX = "peppy"
BOT_NAME = "RealistikBot"

__version__ = "3.1.0"

application = None
db = None
redis = None
config = conf
banchoConf = None
namespace = {}
streams = StreamList()
tokens = TokenList()
channels = ChannelList()
matches = MatchList()
verifiedCache = {}
cached_passwords: dict = {}
chatFilters = None
pool = None
busyThreads = 0

debug = False
restarting = False

startTime = int(time.time())
