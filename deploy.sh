#!/bin/bash

echo "Deploying infrastructure..."
cd terra
terraform init
terraform apply -var-file="terraform.tfvars" -auto-approve

echo "Saving Flask app external IP to flask_app_ip.txt..."
terraform -chdir=terra output -raw flask_app_external_ip > flask_app_ip.txt

echo "Exporting outputs..."
terraform output -json > tf_output.json

# echo "Running Flask app..."
# cd ..
# flask run
