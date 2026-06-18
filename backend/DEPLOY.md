# Drive & Decide — Deploy guide (`template.yaml`)

What the IaC template covers, and what stays manual. The cloud backend MVP has
been deployed from this template in an AWS Academy Learner Lab and works
end-to-end. Device certificates and private keys are deliberately **not** part
of the template — they must never live in Git or CloudFormation.

## 1. What the template creates

| Area | Resource |
|------|----------|
| DynamoDB | table `ParkingStatus` (PK `garageId` S, SK `spotId` N, on-demand) |
| Lambda | `drive-decide-validation` (schema/range check → `update_item`) |
| Lambda | `drive-decide-aggregation` (utilisation + traffic light + API handler) |
| IoT Core | policy `drive-decide-iot-publish-policy` (Connect + Publish only) |
| IoT Core | rule `drive_decide_parking_status_rule` (`SELECT … FROM 'parking/+/spot/+'`) |
| Lambda Permission | IoT Rule may invoke the validation Lambda |
| API Gateway | HTTP API `drive-decide-api` + AWS_PROXY integration to aggregation |
| API Gateway | route `GET /garages/{garageId}/utilization`, `$default` stage (AutoDeploy) |
| Lambda Permission | API Gateway may invoke the aggregation Lambda |
| S3 | website bucket (auto-named) + public-read bucket policy for `web/dist` |
| Outputs | API URL, topic pattern, DynamoDB table name, website bucket + URL |

Resulting backend path:

```text
MQTT topic → IoT Rule → Validation Lambda → DynamoDB → Aggregation Lambda → API Gateway URL
```

## 2. The `TotalSpots` parameter (demo vs. scale)

The template exposes one parameter, `TotalSpots` (default `4`), wired into both
Lambdas:

- **Validation** accepts only `spotId` in `1..TotalSpots` (others return 400 and
  are not stored).
- **Aggregation** computes `utilisation = occupied / TotalSpots`.

| Scenario | Deploy with |
|----------|-------------|
| Physical 4-sensor demo board | `TotalSpots=4` (default) |
| Virtual load generator at scale (Phase 5) | `TotalSpots=200` / `400` / `500` |

> **Why this matters for `virtual/load_generator/`:** at the default of 4, every
> simulated spot beyond 4 is rejected before it reaches DynamoDB, so the stored
> state and the API utilisation are wrong at scale (and DynamoDB write costs are
> undercounted). Set `TotalSpots` to match the load generator's `spots` for each
> measurement run. Because the table is `Retain`/latest-wins, clear it (or use a
> distinct `garageId`) when switching between different spot counts so stale
> spots from a previous run don't inflate the count.

Update the running stack's parameter without touching code, e.g.:

```bash
aws cloudformation deploy \
  --region us-east-1 \
  --stack-name drive-and-decide \
  --template-file backend/template.yaml \
  --parameter-overrides TotalSpots=400 \
  --capabilities CAPABILITY_NAMED_IAM
```

## 3. Before you deploy

- **Region:** in the Learner Lab, deploy to `us-east-1`.
- **Name collisions:** if the resources already exist in the account (e.g. from a
  manual setup), the deploy fails on duplicate names — `ParkingStatus`,
  `drive-decide-validation`, `drive-decide-aggregation`, `drive-decide-api`,
  `drive-decide-iot-publish-policy`, `drive_decide_parking_status_rule`. Either
  delete the existing resources, import them, or rename with a suffix.
- **LabRole:** the template assumes the Learner Lab `LabRole` exists. In a normal
  account, create/reference your own IAM role with equivalent permissions.
- **Table retention:** `ParkingStatus` uses `DeletionPolicy: Retain`, so deleting
  the stack leaves the table behind (which can then cause a name collision on the
  next deploy).

## 4. Manual steps after deploy (per device)

The template creates the IoT **policy** but no certificates. For each device:

1. **Create an IoT thing:** `drive-decide-esp32-a` (later `…-esp32-b`, `…-demo`).
2. **Create + download a certificate:** device certificate, private key, public
   key, and Amazon Root CA 1. The **private key is downloadable only once** —
   never commit, embed in the template, or share it. Set the certificate to
   **Active**.
3. **Attach the policy** `drive-decide-iot-publish-policy` to the certificate.
4. **Attach the certificate** to the thing.
5. **Read the endpoint:** IoT Core → Settings → Device data endpoint
   (`xxxxxxxxxxxxxx-ats.iot.us-east-1.amazonaws.com`).

The policy grants `iot:Connect` + `iot:Publish` to `parking/*/spot/*` only — no
`Subscribe`/`Receive`. That is sufficient for both the ESP32 firmware and the
virtual load generator (both publish-only), and is why the virtual traffic light
reads the REST API instead of subscribing to MQTT.

## 5. Configuring the publishers

- **ESP32 firmware** (`firmware/`): set WiFi, `AWS_IOT_ENDPOINT`, a distinct
  `MQTT_CLIENT_ID`/`SENSOR_ID` (e.g. `esp32-a`), `GARAGE_ID=garage1`, and place
  the cert/key/CA in the gitignored `config.h`/`secrets.h`.
- **Virtual load generator** (`virtual/load_generator/`): copy
  `config.example.ini` → `config.ini`, set the same endpoint, a **distinct**
  `clientId` (e.g. `virtual-loadgen` — IoT Core force-disconnects duplicates),
  and the cert/key/CA paths. Run with `--transport aws`.

Topics are unchanged: `parking/garage1/spot/<spotId>`.

## 6. Tests after deploy

**Validation Lambda** — test event:

```json
{ "sensorId": "manual-test", "garageId": "garage1", "spotId": 1,
  "ts": 1735680000000, "raw": 1, "status": "occupied" }
```
Expect `statusCode 200` and a written/updated DynamoDB item.

**API Gateway** — open the `ApiUrl` output, e.g.
`https://<api-id>.execute-api.us-east-1.amazonaws.com/garages/garage1/utilization`:

```json
{ "garageId": "garage1", "totalSpots": 4, "occupied": 1, "free": 3,
  "utilization": 0.25, "light": "green" }
```

**MQTT test client** — subscribe to `parking/garage1/spot/#`, publish a contract
message to `parking/garage1/spot/1`, then re-check DynamoDB and the API.

**ESP32 / load generator** — with certs, endpoint, and config in place, the full
path `publisher → IoT Core → IoT Rule → Validation → DynamoDB → Aggregation →
API` works.

## 6b. Deploy the web app (`web/dist` → S3)

The template provisions an S3 website bucket and a public-read policy, but the
**bundle is uploaded separately** (CloudFormation doesn't ship file contents).
Because Vite bakes `VITE_API_BASE` in at **build time**, build *after* the stack
exists so the app points at the live API. `web/.env.production` is **gitignored**
and written fresh from the stack's `ApiBase` output on every build — never
hardcode an endpoint there. `deploy.sh` automates steps 1–4 below.

```bash
# 1. Read the two outputs from the deployed stack
API_BASE=$(aws cloudformation describe-stacks --stack-name drive-and-decide --region us-east-1 \
  --query "Stacks[0].Outputs[?OutputKey=='ApiBase'].OutputValue" --output text)
BUCKET=$(aws cloudformation describe-stacks --stack-name drive-and-decide --region us-east-1 \
  --query "Stacks[0].Outputs[?OutputKey=='WebsiteBucketName'].OutputValue" --output text)

# 2. Build with the live endpoint baked in
cd web
echo "VITE_API_BASE=$API_BASE" > .env.production
npm ci && npm run build

# 3. Upload the static bundle
aws s3 sync dist/ "s3://$BUCKET/" --delete

# 4. Open the public URL (WebsiteUrl output)
aws cloudformation describe-stacks --stack-name drive-and-decide --region us-east-1 \
  --query "Stacks[0].Outputs[?OutputKey=='WebsiteUrl'].OutputValue" --output text
```

Re-run steps 2–3 whenever the web app changes. The bucket uses
`DeletionPolicy: Delete`, so deleting the stack removes it (and its contents)
cleanly — unlike the retained DynamoDB table.

> **Learner Lab caveat:** account-level S3 *Block Public Access* can override the
> bucket's own settings. If the `WebsiteUrl` returns 403, the bucket policy is
> fine but public access is blocked at the account level — check S3 → Account
> settings, or fall back to serving the demo via `npm run preview` locally.

## 7. Summary

Template: cloud backend, API Gateway, IoT Rule, IoT policy, Lambda permissions,
DynamoDB table. Manual: IoT thing, device certificate, securing the key/CA,
attaching the policy + certificate, reading the endpoint, flashing/configuring
the publishers. This split keeps device-specific certificates and private keys
out of the IaC template.
