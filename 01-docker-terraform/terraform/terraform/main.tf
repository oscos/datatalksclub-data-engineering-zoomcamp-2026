provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "data_lake" {
  name          = var.gcs_bucket_name
  location      = var.location
  storage_class = var.gcs_storage_class
  force_destroy = true

  uniform_bucket_level_access = true
}

resource "google_bigquery_dataset" "warehouse" {
  dataset_id = var.bq_dataset_name
  location   = var.location
}
