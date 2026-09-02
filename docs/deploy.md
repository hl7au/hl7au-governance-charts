# Deployment

The charts are published into an **existing** HL7 AU CloudFront distribution
(`E3RH4ODMG8LT94`, account `966489602583`) rather than one of their own. There is no
Terraform here: that distribution is not Terraform-managed, and a second state file
describing it would fight whoever changes it next.

```
s3://<origin bucket>/charts/*   ->   https://<distribution>/charts/*
```

## Phase 1 — static charts (all that is needed to see images online)

Eight files plus an index page, published by `.github/workflows/publish.yml`:

```
/charts/cochairs.svg          /charts/projects.svg
/charts/cochairs-dark.svg     /charts/projects-dark.svg
/charts/cochairs-bare.svg     /charts/projects-bare.svg
/charts/cochairs-bare-dark.svg /charts/projects-bare-dark.svg
/charts/index.html
```

Embed one with a plain tag — they send `Access-Control-Allow-Origin: *`:

```html
<img src="https://<distribution>/charts/projects.svg" alt="HL7 AU work groups and projects">
```

### Before the first run, confirm three things about the distribution

The workflow assumes all three. If any is false it will publish to a path nothing serves.

1. **The default cache behaviour's origin is an S3 bucket**, and that bucket is the one
   in `AWS_BUCKET`.
2. **That origin has no origin path** (or, if it does, the `charts/` prefix sits inside
   it — adjust the sync target to match).
3. **Nothing already answers `/charts/*`** on that distribution.

```bash
aws cloudfront get-distribution-config --id E3RH4ODMG8LT94 \
  --query 'DistributionConfig.{Origins:Origins.Items[].{Id:Id,Domain:DomainName,Path:OriginPath},Default:DefaultCacheBehavior.TargetOriginId,Ordered:CacheBehaviors.Items[].PathPattern}'
```

### Secrets

| Secret | Value |
|---|---|
| `AWS_ROLE_ARN` | Deploy role — see `setup-github.md` |
| `AWS_BUCKET` | The distribution's S3 origin bucket |
| `AWS_DISTRIBUTION_ID` | `E3RH4ODMG8LT94` |
| `AWS_LAMBDA_FUNCTION` | Leave unset until phase 2 |

The role's S3 permissions should be scoped to the prefix, not the bucket:

```json
{ "Effect": "Allow",
  "Action": ["s3:PutObject", "s3:DeleteObject"],
  "Resource": "arn:aws:s3:::<bucket>/charts/*" },
{ "Effect": "Allow",
  "Action": ["s3:ListBucket"],
  "Resource": "arn:aws:s3:::<bucket>",
  "Condition": { "StringLike": { "s3:prefix": ["charts/*"] } } }
```

Two safety properties worth preserving if you edit the workflow: the sync's source and
destination are both `charts/`, so `--delete` can only remove a chart the build no longer
produces; and the invalidation is `/charts/*`, not `/*`, so a chart edit does not flush
the rest of the distribution.

## Phase 2 — the `/render/*` endpoint (optional)

Static files cannot answer a query string, so `?groups=`, `?w=` and the rest need the
Lambda. This is additive and can wait.

1. Package and create the function (no dependencies, so no layer):

   ```bash
   zip -qr renderer.zip src lambda_function.py governance.md -x "*/__pycache__/*"
   aws lambda create-function \
     --function-name hl7au-governance-charts-renderer \
     --runtime python3.12 --handler lambda_function.handler \
     --role arn:aws:iam::966489602583:role/<lambda execution role> \
     --zip-file fileb://renderer.zip --timeout 10 --memory-size 256 \
     --region ap-southeast-2
   ```

2. Add a function URL with `--auth-type AWS_IAM`. **Not `NONE`** — that publishes an
   unmetered renderer to the open internet, bypassing the CDN.

3. In the CloudFront console, add the function URL as an origin with an **origin access
   control** of type Lambda, then add a behaviour:

   | Setting | Value |
   |---|---|
   | Path pattern | `/render/*` |
   | Origin | the function URL |
   | Viewer protocol | Redirect HTTP to HTTPS |
   | Allowed methods | GET, HEAD, OPTIONS |
   | Cache policy | Custom: **query strings = all** (the query string *is* the image) |
   | Compress | Yes |

4. Grant CloudFront invoke rights:

   ```bash
   aws lambda add-permission --function-name hl7au-governance-charts-renderer \
     --statement-id AllowCloudFront --action lambda:InvokeFunctionUrl \
     --principal cloudfront.amazonaws.com \
     --source-arn arn:aws:cloudfront::966489602583:distribution/E3RH4ODMG8LT94 \
     --function-url-auth-type AWS_IAM --region ap-southeast-2
   ```

5. Set the `AWS_LAMBDA_FUNCTION` secret. The workflow's Lambda step and the `/render/*`
   invalidation switch themselves on once it exists.

## Local

```bash
python serve.py          # http://127.0.0.1:8000
```

Same routes, `no-store` so an edit to `governance.md` shows on refresh.
