from __future__ import annotations

from constants import clientPackets
from helpers import chatHelper as chat
from objects import glob


def handle(userToken, packetData):
    packetData = clientPackets.tournamentLeaveMatchChannel(packetData)
    matchID = packetData["matchID"]
    if matchID not in glob.matches.matches or not userToken.tournament:
        return
    chat.partChannel(token=userToken, channel=f"#multi_{matchID}", force=True)
    userToken.matchID = 0
