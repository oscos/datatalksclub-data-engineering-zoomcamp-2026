variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-west2"
}

variable "location" {
  description = "GCP multi-region location"
  type        = string
  default     = "US"
}

variable "gcs_bucket_name" {
  description = "GCS bucket for data lake"
  type        = string
}

variable "gcs_storage_class" {
  description = "Storage class for GCS bucket"
  type        = string
  default     = "STANDARD"
}

variable "bq_dataset_name" {
  description = "BigQuery dataset name"
  type        = string
}
