# Signature integration

The frontend will request a signing session from Signature Service, present certificate metadata, show the digest, accept confirmation and poll or subscribe for the verification result. It never handles private keys.

Mock mode will produce deterministic signed metadata and an audit event. Production mode requires server-side identity, certificate validation, timestamping and immutable signed-file storage.
