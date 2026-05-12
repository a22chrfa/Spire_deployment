# We import os to be able to set socket path (i.e. communicate with the workload API of the agent)
import os

# To be able to print date and time
from datetime import datetime

# The spiffe library is needed to talk to the spire-agent and receive the certificate
from spiffe import SpiffeId
from spiffe import X509Source

# These imports are needed to set up a port for the other workload to contact us, and to use mTLS
from spiffetls import listen
from spiffetls import ListenOptions 
from spiffetls.mode import ServerTlsMode
from spiffetls.tlsconfig.authorize import authorize_id

# We tell the application which socket to use to contact the agent.
os.environ["SPIFFE_ENDPOINT_SOCKET"] = "unix:///run/spire/sockets/agent.sock"

# We add some logging that will be visible in powershell. We force it to be written immediately with flush.
print("Log: Workload 1 is starting", flush=True)

# We run the function from the spiffe library, which fetches the cert
x509_source = X509Source()
print("X509Source created", flush=True)

# Now we set up what to listen for. We enforce mTLS and a specific spiffe ID (the other workload)
options = ListenOptions(
    tls_mode=ServerTlsMode.MTLS,
    authorize_fn=authorize_id(SpiffeId("spiffe://nonanonymous.org/ns/default/sa/workload2")),
)

# We start listening on port 8443 (no reason for the specific port, just convention)
listener = listen("0.0.0.0:8443", x509_source, options)
print("Server listening on port 8443", flush=True)

# We start an infinite loop to keep the script running. We accept connections and store both return values. We then store the message in "data". We then print the message, respond, and then close the connection. Since the loop is infinite however, we still react to new connections. 
while True:
    conn, addr = listener.accept()
    reponse = conn.recv(1024)
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Received mTLS connection from workload 2: {reponse.decode()}", flush=True)
    conn.sendall(b"Hello from workload1")
    conn.close()