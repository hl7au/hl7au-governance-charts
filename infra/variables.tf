variable "project_name" {
  description = "Prefix for every resource name."
  type        = string
  default     = "hl7au-governance-charts"
}

variable "region" {
  description = "Region for S3 and Lambda. CloudFront is global."
  type        = string
  default     = "ap-southeast-2"
}

variable "domain_names" {
  description = "Optional CNAMEs, e.g. [\"charts.hl7.au\"]. Requires certificate_arn."
  type        = list(string)
  default     = []
}

variable "certificate_arn" {
  description = "ACM certificate ARN. Must be issued in us-east-1 for CloudFront."
  type        = string
  default     = null
}

variable "price_class" {
  description = "PriceClass_100 is North America + Europe; _All includes Australia."
  type        = string
  default     = "PriceClass_All"
}

variable "tags" {
  type    = map(string)
  default = {}
}
