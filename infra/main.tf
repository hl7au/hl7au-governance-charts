terraform {
  required_version = ">= 1.5"
  required_providers {
    aws     = { source = "hashicorp/aws", version = "~> 5.0" }
    archive = { source = "hashicorp/archive", version = "~> 2.4" }
  }
}

provider "aws" {
  region = var.region
}

locals {
  name = var.project_name
  tags = merge({ Project = var.project_name, ManagedBy = "terraform" }, var.tags)
}

# ---------------------------------------------------------------------------
# S3 — the fixed-URL charts and the index page. Private; reached only through
# CloudFront via origin access control.
# ---------------------------------------------------------------------------
resource "aws_s3_bucket" "site" {
  bucket = "${local.name}-site"
  tags   = local.tags
}

resource "aws_s3_bucket_public_access_block" "site" {
  bucket                  = aws_s3_bucket.site.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "site" {
  bucket = aws_s3_bucket.site.id
  versioning_configuration { status = "Enabled" }
}

data "aws_iam_policy_document" "site" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.site.arn}/*"]
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.charts.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "site" {
  bucket = aws_s3_bucket.site.id
  policy = data.aws_iam_policy_document.site.json
}

# ---------------------------------------------------------------------------
# Lambda — the parameterised /render/* endpoint. Bundles the renderer and
# governance.md, so publishing new content updates both origins.
# ---------------------------------------------------------------------------
data "archive_file" "renderer" {
  type        = "zip"
  output_path = "${path.module}/.build/renderer.zip"

  source_dir = "${path.module}/.."
  excludes = [
    "infra", "out", "site", "docs", ".git", ".github",
    "__pycache__", "src/__pycache__", "src/diagrams/__pycache__",
    "README.md", "CLAUDE.md", "serve.py", "build.py",
  ]
}

data "aws_iam_policy_document" "assume_lambda" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "renderer" {
  name               = "${local.name}-renderer"
  assume_role_policy = data.aws_iam_policy_document.assume_lambda.json
  tags               = local.tags
}

resource "aws_iam_role_policy_attachment" "renderer_logs" {
  role       = aws_iam_role.renderer.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "renderer" {
  function_name    = "${local.name}-renderer"
  role             = aws_iam_role.renderer.arn
  handler          = "lambda_function.handler"
  runtime          = "python3.12"
  filename         = data.archive_file.renderer.output_path
  source_code_hash = data.archive_file.renderer.output_base64sha256
  memory_size      = 256
  timeout          = 10
  tags             = local.tags
}

resource "aws_lambda_function_url" "renderer" {
  function_name      = aws_lambda_function.renderer.function_name
  authorization_type = "AWS_IAM" # only CloudFront, signed via OAC
}

resource "aws_lambda_permission" "cloudfront" {
  statement_id           = "AllowCloudFrontInvoke"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = aws_lambda_function.renderer.function_name
  principal              = "cloudfront.amazonaws.com"
  source_arn             = aws_cloudfront_distribution.charts.arn
  function_url_auth_type = "AWS_IAM"
}
