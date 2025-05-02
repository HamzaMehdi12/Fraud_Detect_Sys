module "fraud_staging" {
  source = "../../modules/aws"

  environment = "staging"
  vpc_cidr    = "10.1.0.0/16"
  instance_type = "m5.large"
  min_nodes    = 1
  max_nodes    = 3
  model_bucket = "fraud-models-staging"
}