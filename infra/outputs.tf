output "distribution_domain" {
  description = "Embed base URL, e.g. https://d111111abcdef8.cloudfront.net"
  value       = "https://${aws_cloudfront_distribution.charts.domain_name}"
}

output "distribution_id" {
  description = "Pass to `aws cloudfront create-invalidation` after a publish."
  value       = aws_cloudfront_distribution.charts.id
}

output "bucket_name" {
  value = aws_s3_bucket.site.id
}

output "lambda_function_name" {
  value = aws_lambda_function.renderer.function_name
}
