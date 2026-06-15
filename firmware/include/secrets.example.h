#pragma once
// AWS IoT Core device-credential template. COMMITTED.
// Copy this file to secrets.h (gitignored) and paste the cert / key / root CA
// you downloaded when you created the IoT thing. NEVER commit the real secrets.h.

// AmazonRootCA1.pem
static const char AWS_ROOT_CA[] PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----
PASTE_AmazonRootCA1.pem_HERE
-----END CERTIFICATE-----
)EOF";

// device-certificate.pem.crt
static const char DEVICE_CERT[] PROGMEM = R"KEY(
-----BEGIN CERTIFICATE-----
PASTE_device-certificate.pem.crt_HERE
-----END CERTIFICATE-----
)KEY";

// private.pem.key
static const char DEVICE_PRIVATE_KEY[] PROGMEM = R"KEY(
-----BEGIN RSA PRIVATE KEY-----
PASTE_private.pem.key_HERE
-----END RSA PRIVATE KEY-----
)KEY";
