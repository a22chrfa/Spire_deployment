# We import os to be able to set socket path (i.e. communicate with the workload API of the agent)
import os

# To be able to print date and time
from datetime import datetime

# time is just for the sleep function (intermittent messaging ever 5th second)
import time

# These imports are needed to contact the other workload, and to use mTLS
from spiffe import SpiffeId, X509Source
from spiffetls import dial
from spiffetls.tlsconfig.authorize import authorize_id

# We tell the application which socket to use to contact the agent.
os.environ["SPIFFE_ENDPOINT_SOCKET"] = "unix:///run/spire/sockets/agent.sock"
print("Log: Workload 2 is starting", flush=True)

# We run the function from the spiffe library, which fetches the cert
x509_source = X509Source()
print("X509Source created", flush=True)

# An infinite loop with sleep for intermittent messaging. We create a connection object containing the result of the dial function (which is the connection), where workload1 is resolved by kubernetes internal dns.
# We then use the connection to send the message, and we also store and print the response. We then close connection, waiting for the next iteration of the loop.
while True:
        conn = dial(
            "workload1:8443",
            x509_source,
            authorize_fn=authorize_id(SpiffeId("spiffe://nonanonymous.org/ns/default/sa/workload1")),
        )
        conn.sendall(b"Hello from workload2")
        response = conn.recv(1024)
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Received mTLS connection from workload 1: {response.decode()}", flush=True)
        conn.close()
        time.sleep(5)