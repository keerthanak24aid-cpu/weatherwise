from pyngrok import ngrok
import time

# start an HTTP tunnel on port 5000
tunnel = ngrok.connect(5000, "http")
print("NGROK_URL:" + tunnel.public_url, flush=True)
try:
    while True:
        time.sleep(3600)
except KeyboardInterrupt:
    ngrok.disconnect(tunnel.public_url)
