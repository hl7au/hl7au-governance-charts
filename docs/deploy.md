# Deployment

The charts are published into an **existing** HL7 AU CloudFront distribution rather than
one of their own. There is no Terraform here: that distribution is not Terraform-managed,
and a second state file describing it would fight whoever changes it next.

| | |
|---|---|
| Distribution | `E3RH4ODMG8LT94` — named `hl7austaging` |
| Account | `966489602583` |
| Public URL | **https://apps.hl7.org.au** (also `d14vlf5der2w6d.cloudfront.net`) |
| S3 origin | `hl7auprojects` (ap-southeast-2), **origin path `/site`** |
| Other origin | `inferno.hl7.org.au`, serving `/aucore-verified/api/*` |

**The origin path is the thing to remember.** A viewer request for `/charts/x.svg` is
fetched from `s3://hl7auprojects/site/charts/x.svg`. Publishing to `charts/` at the bucket
root uploads successfully and serves nothing — the workflow's `S3_PREFIX` is
`site/charts` for exactly this reason.

```
s3://hl7auprojects/site/charts/*   ->   https://apps.hl7.org.au/charts/*
```

The bucket also holds the `aucore-verified` site, so both the sync and the deploy role
stay scoped to the prefix.

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
<img src="https://apps.hl7.org.au/charts/projects.svg" alt="HL7 AU work groups and projects">
```

### Distribution state as read on 2 September 2026

| Precedence | Path pattern | Origin | Cache policy |
|---|---|---|---|
| 0 | `/aucore-verified/api/*` | inferno.hl7.org.au | CachingDisabled |
| 1 | `/aucore-verified` | S3 | CachingDisabled |
| 2 | `/aucore-verified/*` | S3 | CachingDisabled |
| 3 | Default `(*)` | S3 | CachingDisabled |

Nothing answers `/charts/*`, so the charts land on the default behaviour and are served
from the S3 origin with no extra configuration. Re-check before assuming this still holds:

```bash
aws cloudfront get-distribution-config --id E3RH4ODMG8LT94 \
  --query 'DistributionConfig.{Origins:Origins.Items[].{Id:Id,Domain:DomainName,Path:OriginPath},Default:DefaultCacheBehavior.TargetOriginId,Ordered:CacheBehaviors.Items[].PathPattern}'
```

### Recommended, not required: a caching behaviour for `/charts/*`

Every behaviour on this distribution uses **Managed-CachingDisabled**, which is a
reasonable default for an app but means each chart request goes to S3 and the
`s-maxage` the workflow sets is ignored at the edge. The charts are static files that
change on a commit, so they are a poor fit for that.

Adding one behaviour fixes it without touching anything already there:

| Setting | Value |
|---|---|
| Path pattern | `/charts/*` |
| Origin | `hl7auprojects.s3.ap-southeast-2.amazonaws.com` |
| Viewer protocol | Redirect HTTP to HTTPS |
| Cache policy | `Managed-CachingOptimized` |
| Compress | Yes |

Put it above the default. The workflow already invalidates `/charts/*` on every publish,
so a cached chart is never stale for long. Without this the images still work — they are
just uncached.

### Secrets

| Secret | Value |
|---|---|
| `AWS_ROLE_ARN` | Deploy role — see `setup-github.md` |
| `AWS_BUCKET` | `hl7auprojects` |
| `AWS_DISTRIBUTION_ID` | `E3RH4ODMG8LT94` |
| `AWS_LAMBDA_FUNCTION` | Leave unset until phase 2 |

The role's S3 permissions should be scoped to the prefix, not the bucket:

```json
{ "Effect": "Allow",
  "Action": ["s3:PutObject", "s3:DeleteObject"],
  "Resource": "arn:aws:s3:::hl7auprojects/site/charts/*" },
{ "Effect": "Allow",
  "Action": ["s3:ListBucket"],
  "Resource": "arn:aws:s3:::hl7auprojects",
  "Condition": { "StringLike": { "s3:prefix": ["site/charts/*"] } } }
```

That scoping is doing real work: the bucket also serves the `aucore-verified` site, and a
role that could write the whole bucket is one `--delete` mistake away from removing it.

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
