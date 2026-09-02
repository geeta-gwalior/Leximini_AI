variable "gcp_project_id" {
  description = "Google Cloud Platform Project ID"
  type        = string
  default     = "leximini-ai-gcp-project"
}

variable "gcp_region" {
  description = "GCP Deployment Region"
  type        = string
  default     = "asia-south1" # Mumbai, India
}

variable "environment" {
  description = "Environment stage (dev, staging, prod)"
  type        = string
  default     = "prod"
}
