#!/usr/bin/env bash
#
# deploy.sh — Drive & Decide: one-shot deploy into a FRESH, EMPTY AWS Learner Lab.
#
# Precondition: you have already pasted current Learner Lab credentials
# (AWS Details -> "AWS CLI: Show") into ~/.aws/credentials or exported them, so
# the AWS CLI is authenticated. This script assumes the account is EMPTY — it
# does not clean up an existing stack or hand-made resources.
#
# What it does:
#   1. verifies prerequisites + credentials
#   2. deploys backend/template.yaml (DynamoDB, Lambdas, IoT rule/policy,
#      API Gateway, S3 website bucket — everything)
#   3. reads the stack outputs
#   4. builds the web app with the live API baked in (VITE_API_BASE)
#   5. uploads web/dist to the S3 website bucket
#   6. prints the public website URL
#
# Override via env vars:
#   REGION (us-east-1)   STACK_NAME (drive-and-decide)
#   TOTAL_SPOTS (4)      GARAGE_SPOTS ('{"garage1":4,"garage2":400}')
#
# Usage:  ./deploy.sh
set -euo pipefail

# Run from the repo root (the directory this script lives in), so the relative
# paths below work no matter where it's invoked from.
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

REGION="${REGION:-${AWS_DEFAULT_REGION:-us-east-1}}"
STACK_NAME="${STACK_NAME:-drive-and-decide}"
TOTAL_SPOTS="${TOTAL_SPOTS:-4}"
if [ -z "${GARAGE_SPOTS:-}" ]; then
  GARAGE_SPOTS='{"garage1":4,"garage2":400}'
fi

fail() { echo "ERROR: $*" >&2; exit 1; }

# --- 1. prerequisites + credentials -----------------------------------------
command -v aws >/dev/null 2>&1 || fail "aws CLI not found on PATH."
command -v npm >/dev/null 2>&1 || fail "npm not found on PATH (needed to build the web app)."
[ -f backend/template.yaml ] || fail "backend/template.yaml not found — is this the repo root?"

echo "==> Checking AWS credentials (region: $REGION)..."
ACCOUNT="$(aws sts get-caller-identity --query Account --output text 2>/dev/null)" \
  || fail "AWS credentials not working. Paste fresh Learner Lab credentials and retry."
[ -n "$ACCOUNT" ] || fail "AWS credentials not working. Paste fresh Learner Lab credentials and retry."
echo "    Account: $ACCOUNT"

# --- 2. deploy the stack ----------------------------------------------------
echo "==> Deploying stack '$STACK_NAME' (TotalSpots=$TOTAL_SPOTS, GarageSpots=$GARAGE_SPOTS)..."
set +e
deploy_out="$(aws cloudformation deploy \
  --region "$REGION" \
  --stack-name "$STACK_NAME" \
  --template-file backend/template.yaml \
  --parameter-overrides "TotalSpots=$TOTAL_SPOTS" "GarageSpots=$GARAGE_SPOTS" \
  --capabilities CAPABILITY_NAMED_IAM 2>&1)"
deploy_rc=$?
set -e
echo "$deploy_out"
# "No changes to deploy" is a non-zero exit but not an error (lets you re-run).
if [ $deploy_rc -ne 0 ] && ! echo "$deploy_out" | grep -q "No changes to deploy"; then
  fail "CloudFormation deploy failed (see output above)."
fi

# --- 3. read stack outputs --------------------------------------------------
get_output() {
  aws cloudformation describe-stacks --region "$REGION" --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text
}
echo "==> Reading stack outputs..."
API_BASE="$(get_output ApiBase)"
BUCKET="$(get_output WebsiteBucketName)"
WEBSITE_URL="$(get_output WebsiteUrl)"
{ [ -n "$API_BASE" ] && [ "$API_BASE" != "None" ]; } || fail "Could not read ApiBase output."
{ [ -n "$BUCKET" ]   && [ "$BUCKET"   != "None" ]; } || fail "Could not read WebsiteBucketName output."
echo "    ApiBase: $API_BASE"
echo "    Bucket:  $BUCKET"

# --- 4. build the web app with the live API baked in ------------------------
# NOTE: the app reads VITE_API_BASE (base URL, no path) — see web/src/config.js.
# This overwrites the committed web/.env.production (which points at another API).
echo "==> Building web app (VITE_API_BASE=$API_BASE)..."
printf 'VITE_API_BASE=%s\n' "$API_BASE" > web/.env.production
( cd web && npm ci && npm run build )

# --- 5. upload the static bundle to S3 --------------------------------------
echo "==> Uploading web/dist to s3://$BUCKET ..."
aws s3 sync web/dist/ "s3://$BUCKET/" --region "$REGION" --delete

# --- 6. done ----------------------------------------------------------------
echo ""
echo "==> Done. Website: $WEBSITE_URL"
echo "    If it returns 403, account-level S3 Block Public Access is on"
echo "    (see backend/DEPLOY.md §6b) — fall back to:  cd web && npm run preview"
