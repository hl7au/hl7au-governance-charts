# Putting this on GitHub with automatic deployment

The workflow already exists (`.github/workflows/publish.yml`). What it needs is a repo,
four secrets, and an AWS role it is allowed to assume. Repo visibility is irrelevant to
the published charts — they are served from CloudFront, not from GitHub — so a private
repo is fine.

## 1. Repo

```bash
cd C:\repos\hl7au-governance-charts
git commit -m "HL7 AU governance charts: markdown-driven SVG generator"
gh repo create hl7au/hl7au-governance-charts --private --source . --remote origin --push
```

Everything is already staged. If you don't use `gh`, create the repo in the UI and:

```bash
git remote add origin git@github.com:hl7au/hl7au-governance-charts.git
git push -u origin main
```

## 2. Infrastructure

```bash
cd infra
terraform init
terraform validate      # never run — see docs/session-history.md
terraform apply
terraform output
```

Keep the four outputs; three of them become secrets below.

## 3. The deploy role

GitHub authenticates to AWS by OIDC, so there are no long-lived keys to rotate. If the
account already has the GitHub OIDC provider (the permalinks setup uses this pattern),
reuse it — one provider per account is the limit anyway.

Trust policy — note `ref:refs/heads/main`, which stops a branch or a fork's PR from
assuming the role:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::<account>:oidc-provider/token.actions.githubusercontent.com" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
        "token.actions.githubusercontent.com:sub": "repo:hl7au/hl7au-governance-charts:ref:refs/heads/main"
      }
    }
  }]
}
```

Permissions policy — exactly what the workflow does, nothing more:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::hl7au-governance-charts-site" },
    { "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::hl7au-governance-charts-site/*" },
    { "Effect": "Allow",
      "Action": ["lambda:UpdateFunctionCode", "lambda:GetFunction",
                 "lambda:GetFunctionConfiguration"],
      "Resource": "arn:aws:lambda:ap-southeast-2:<account>:function:hl7au-governance-charts-renderer" },
    { "Effect": "Allow",
      "Action": ["cloudfront:CreateInvalidation"],
      "Resource": "arn:aws:cloudfront::<account>:distribution/<distribution id>" }
  ]
}
```

## 4. Secrets

`Settings → Secrets and variables → Actions`, or:

```bash
gh secret set AWS_ROLE_ARN            --body "arn:aws:iam::<account>:role/<role name>"
gh secret set AWS_BUCKET              --body "$(terraform -chdir=infra output -raw bucket_name)"
gh secret set AWS_LAMBDA_FUNCTION     --body "$(terraform -chdir=infra output -raw lambda_function_name)"
gh secret set AWS_DISTRIBUTION_ID     --body "$(terraform -chdir=infra output -raw distribution_id)"
```

## 5. From then on

Edit `governance.md`, commit, push to `main`. The workflow builds, checks every SVG
parses, syncs S3, updates the Lambda and invalidates CloudFront. `gh run watch` follows it.

`workflow_dispatch` is enabled, so you can also republish without a content change —
useful after a `terraform apply` that replaced the distribution.

## Worth knowing

- The workflow only fires on changes to `governance.md`, `src/**`, `build.py`,
  `lambda_function.py` or itself. A README edit deploys nothing, on purpose.
- It updates **both** origins. S3 alone would leave `/render/*` serving stale content,
  because the Lambda bundles `governance.md`.
- `concurrency: publish` with `cancel-in-progress` means two quick pushes won't race each
  other into a half-synced bucket.
