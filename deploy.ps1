<#
.SYNOPSIS
Deploy Drive & Decide from Windows PowerShell.

.DESCRIPTION
Runs the same one-shot flow as deploy.sh, but in PowerShell:
1. verify prerequisites and AWS credentials
2. deploy backend/template.yaml
3. read stack outputs
4. build the web app with VITE_API_BASE injected for Vite
5. sync web/dist to the S3 website bucket
6. print the public website URL

Run from anywhere:
  powershell -File .\deploy.ps1
#>

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoRoot = Split-Path -Parent $PSCommandPath
Set-Location -Path $RepoRoot

$Region = if ([string]::IsNullOrWhiteSpace($env:REGION)) { $env:AWS_DEFAULT_REGION } else { $env:REGION }
if ([string]::IsNullOrWhiteSpace($Region)) { $Region = 'us-east-1' }

$StackName = if ([string]::IsNullOrWhiteSpace($env:STACK_NAME)) { 'drive-and-decide' } else { $env:STACK_NAME }
$TotalSpots = if ([string]::IsNullOrWhiteSpace($env:TOTAL_SPOTS)) { '4' } else { $env:TOTAL_SPOTS }
$GarageSpots = if ([string]::IsNullOrWhiteSpace($env:GARAGE_SPOTS)) { '{"garage1":4,"garage2":400}' } else { $env:GARAGE_SPOTS }

$BackendTemplate = Join-Path (Join-Path $RepoRoot 'backend') 'template.yaml'
$WebDir = Join-Path $RepoRoot 'web'

function Fail {
    param([string]$Message)
    throw "ERROR: $Message"
}

function Assert-ExitCode {
    param(
        [int]$ExitCode,
        [string]$Message
    )

    if ($ExitCode -ne 0) {
        Fail $Message
    }
}

function Get-StackOutput {
    param([string]$OutputKey)

    $args = @(
        'cloudformation', 'describe-stacks',
        '--region', $Region,
        '--stack-name', $StackName,
        '--query', "Stacks[0].Outputs[?OutputKey=='$OutputKey'].OutputValue",
        '--output', 'text'
    )

    $value = & aws @args 2>$null
    if ($LASTEXITCODE -ne 0) {
        return ''
    }

    return (($value | Out-String).Trim())
}

try {
    if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
        Fail 'aws CLI not found on PATH.'
    }

    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        Fail 'npm not found on PATH (needed to build the web app).'
    }

    if (-not (Test-Path -Path $BackendTemplate)) {
        Fail 'backend/template.yaml not found - is this the repo root?'
    }

    Write-Host "==> Checking AWS credentials (region: $Region)..."
    $account = & aws sts get-caller-identity --query Account --output text 2>$null
    $accountExit = $LASTEXITCODE
    $account = (($account | Out-String).Trim())

    if ($accountExit -ne 0 -or [string]::IsNullOrWhiteSpace($account)) {
        Fail 'AWS credentials not working. Paste fresh Learner Lab credentials and retry.'
    }

    Write-Host "    Account: $account"

    Write-Host "==> Deploying stack '$StackName' (TotalSpots=$TotalSpots, GarageSpots=$GarageSpots)..."
    $deployArgs = @(
        'cloudformation', 'deploy',
        '--region', $Region,
        '--stack-name', $StackName,
        '--template-file', $BackendTemplate,
        '--parameter-overrides', "TotalSpots=$TotalSpots", "GarageSpots=$GarageSpots",
        '--capabilities', 'CAPABILITY_NAMED_IAM'
    )

    $deployOut = & aws @deployArgs 2>&1
    $deployExit = $LASTEXITCODE
    $deployText = ($deployOut | Out-String)
    Write-Host $deployText

    if ($deployExit -ne 0 -and $deployText -notmatch 'No changes to deploy') {
        Fail 'CloudFormation deploy failed (see output above).'
    }

    Write-Host '==> Reading stack outputs...'
    $apiBase = Get-StackOutput 'ApiBase'
    $bucket = Get-StackOutput 'WebsiteBucketName'
    $websiteUrl = Get-StackOutput 'WebsiteUrl'

    if ([string]::IsNullOrWhiteSpace($apiBase) -or $apiBase -eq 'None') {
        Fail 'Could not read ApiBase output.'
    }

    if ([string]::IsNullOrWhiteSpace($bucket) -or $bucket -eq 'None') {
        Fail 'Could not read WebsiteBucketName output.'
    }

    Write-Host "    ApiBase: $apiBase"
    Write-Host "    Bucket:  $bucket"

    Write-Host "==> Building web app (VITE_API_BASE=$apiBase)..."
    $previousViteApiBase = $env:VITE_API_BASE
    $env:VITE_API_BASE = $apiBase

    Push-Location -Path $WebDir
    try {
        & npm ci
        Assert-ExitCode $LASTEXITCODE 'npm ci failed.'

        & npm run build
        Assert-ExitCode $LASTEXITCODE 'npm run build failed.'
    }
    finally {
        Pop-Location
        $env:VITE_API_BASE = $previousViteApiBase
    }

    Write-Host "==> Uploading web\dist to s3://$bucket ..."
    $syncArgs = @(
        's3', 'sync',
        (Join-Path $WebDir 'dist'),
        "s3://$bucket/",
        '--region', $Region,
        '--delete'
    )

    & aws @syncArgs
    Assert-ExitCode $LASTEXITCODE 'S3 sync failed.'

    Write-Host ''
    Write-Host "==> Done. Website: $websiteUrl"
    Write-Host '    If it returns 403, account-level S3 Block Public Access is on'
    Write-Host '    (see backend\DEPLOY.md section 6b) - fall back to:  cd web; npm run preview'
}
catch {
    Write-Error $_
    exit 1
}
