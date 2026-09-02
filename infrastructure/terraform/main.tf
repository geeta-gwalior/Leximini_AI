terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# 1. Enable Required GCP APIs
resource "google_project_service" "artifactregistry_api" {
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "run_api" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "sql_api" {
  service            = "sqladmin.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "redis_api" {
  service            = "redis.googleapis.com"
  disable_on_destroy = false
}

# 2. Artifact Registry Docker Repository
resource "google_artifact_registry_repository" "leximini_repo" {
  depends_on    = [google_project_service.artifactregistry_api]
  location      = var.gcp_region
  repository_id = "leximini-containers"
  description   = "Docker Repository for LexiMini AI Microservices"
  format        = "DOCKER"
}

# 3. Cloud SQL PostgreSQL Instance
resource "google_sql_database_instance" "postgres_instance" {
  depends_on       = [google_project_service.sql_api]
  name             = "leximini-postgres-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.gcp_region

  settings {
    tier = "db-f1-micro"
    backup_configuration {
      enabled = true
    }
  }
}

resource "google_sql_database" "database" {
  name     = "leximinidb"
  instance = google_sql_database_instance.postgres_instance.name
}

# 4. Cloud Run Gateway Service
resource "google_cloud_run_v2_service" "gateway_service" {
  depends_on = [google_project_service.run_api, google_artifact_registry_repository.leximini_repo]
  name       = "leximini-gateway"
  location   = var.gcp_region
  ingress    = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.leximini_repo.repository_id}/gateway:latest"
      resources {
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
      }
    }
  }
}
