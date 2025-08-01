#!/bin/bash
# Start Tor safely with a custom config if present
TOR_CONFIG="/opt/osint-vps/routing/tor/torrc"
if [ -f "$TOR_CONFIG" ]; then
    tor -f "$TOR_CONFIG"
else
    tor
fi
