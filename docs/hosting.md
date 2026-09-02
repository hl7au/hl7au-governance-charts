# Hosting

Two ways to reach the same renderer, behind one CloudFront distribution:

| Path | Origin | For |
|---|---|---|
| `/charts/cochairs.svg` | S3 | Fixed URLs. Built by CI, cached hard, nothing to run. |
| `/render/cochairs.svg?...` | Lambda | Anything with a query string. |

Both are `<img src>`-able and both send `Access-Control-Allow-Origin: *`.

```html
<img src="https://charts.example/charts/projects.svg" alt="HL7 AU work groups and projects">
<img src="https://charts.example/render/cochairs.svg?groups=fhir,aucore&dark=1" alt="...">
```

## Parameters

`groups`, `dark`, `header`, `w`, `transparent`, `date`, `title` — see the index page
the distribution serves at `/`, or `src/options.py`.

Only four combinations get static URLs (`charts/<name>{,-dark,-bare,-bare-dark}.svg`).
Everything else goes through `/render/`. If a particular variant becomes load-bearing for
a page, add it to `SITE_VARIANTS` in `build.py` and it becomes a static object too.

## Standing it up

```bash
cd infra
terraform init
terraform apply            # -var 'domain_names=["charts.hl7.au"]' -var certificate_arn=...
terraform output
```

Notes:

- The certificate for a custom domain **must** be issued in `us-east-1`, whatever region
  the rest lives in. That is a CloudFront constraint, not a choice.
- The Lambda function URL is `AWS_IAM`, signed by CloudFront through origin access
  control, so the function URL is not usable directly. Don't relax it to `NONE`: that
  puts an unmetered renderer on the open internet.
- `price_class` defaults to `PriceClass_All` because the audience is in Australia and
  `PriceClass_100` has no Australian edge.

## Publishing

`.github/workflows/publish.yml` runs on any push to `main` that touches the content or
the renderer. It builds the site, checks every SVG parses, syncs to S3 with the right
content types, updates the Lambda (which bundles `governance.md`), and invalidates.

Repository secrets it needs:

| Secret | From |
|---|---|
| `AWS_ROLE_ARN` | An IAM role trusting GitHub's OIDC provider for this repo |
| `AWS_BUCKET` | `terraform output bucket_name` |
| `AWS_LAMBDA_FUNCTION` | `terraform output lambda_function_name` |
| `AWS_DISTRIBUTION_ID` | `terraform output distribution_id` |

The Terraform does not create the OIDC role — the permalinks repo already has that
pattern; reuse it rather than growing a second one.

## Local

```bash
python serve.py          # http://127.0.0.1:8000
```

Serves the same routes as the distribution, including `/`. `governance.md` is re-read
when it changes, so edit and refresh.
