module "fraud_prod" {
  source = "../../modules/aws"

  environment = "prod"
  vpc_cidr    = "10.0.0.0/16"
  instance_type = "m5.2xlarge"
  min_nodes    = 3
  max_nodes    = 10
  model_bucket = "fraud-models-prod"
}