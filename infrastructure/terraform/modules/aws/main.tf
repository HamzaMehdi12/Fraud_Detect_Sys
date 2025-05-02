provider "aws" {
  region = var.region
}

resource "aws_s3_bucket" "model_registry" {
  bucket = "fraud-models-${var.environment}"
  acl    = "private"

  versioning {
    enabled = true
  }
}

resource "aws_eks_cluster" "fraud_cluster" {
  name     = "fraud-${var.environment}"
  role_arn = aws_iam_role.eks_cluster.arn

  vpc_config {
    subnet_ids = var.subnet_ids
  }
}