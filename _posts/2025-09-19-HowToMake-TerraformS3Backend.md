---
title: "How To Make Terraform S3 Backend using Terraform"
author: cilgin
date: 2025-09-19 22:23:07 +0300
categories: [IaC, DevOps, Cloud]
tags: [Terraform, S3, AWS]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-09-19-HowToMake-TerraformS3Backend/main.svg
---

Hello there!

Ever found yourself in a bit of a pickle with Terraform state management, especially when working with a team or CI/CD? You're not alone! In this guide, we're going to walk through how to set up a super robust and reliable Terraform state management backend using AWS S3 for storage and DynamoDB for state locking.

### Why Even Bother with a Remote Backend?

You might be thinking, "Hey, my local `terraform.tfstate` file works just fine!" And you'd be right... if you're a lone wolf 😥 and not running Terraform through any CI/CD pipelines.

But if you're collaborating with teammates or deploying via CI/CD, relying on local state is like building a house on quicksand. Things can get unstable, and those state files can clash in the long run, leading to all sorts of headaches. This is why solutions like Terraform Cloud or an S3 backend are crucial!

So, our game plan is simple: we'll upload that precious `tfstate` file to an S3 bucket for safe keeping, and then use DynamoDB to magically handle state locking, preventing any messy conflicts.

Let's get started!

### Setting Up Our Backend Infrastructure

First things first, you'll need to have your AWS environment configured. I'm hoping you're already a pro at this part!

To provision the S3 bucket and DynamoDB table for your state backend, create a new, temporary directory (e.g., `terraform-backend-setup`). Inside this directory, create the following files:

#### `main.tf`

This file defines the required AWS provider.

```terraform
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.14" # Use a compatible version
    }
  }
}

provider "aws" {
  region = var.aws_region
}
```

#### `variables.tf`

Here we define the input variables for our backend resources.

```terraform
variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "eu-west-1" # Change to your preferred region
}

variable "bucket_name" {
  description = "Name of the s3 bucket name MUST BE UNIQ"
  type        = string
}

variable "dynamodb_name" {
  description = "Name of the dynamodb table name"
  type        = string
  default     = "terraform-locks" # Default name for the lock table
}
```

#### `s3.tf`

This file configures our S3 bucket, including versioning, server-side encryption, and public access blocks for security.

```terraform
resource "aws_s3_bucket" "tf_state" {
  bucket = var.bucket_name

  tags = {
    Name = "Terraform State Bucket"
  }
}

resource "aws_s3_bucket_versioning" "tf_state_versioning" {
  bucket = aws_s3_bucket.tf_state.id

  versioning_configuration {
    status = "Enabled" # Highly recommended for state file recovery!
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tf_state_sse" {
  bucket = aws_s3_bucket.tf_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256" # Encrypts state files at rest
    }
  }
}

resource "aws_s3_bucket_public_access_block" "tf_state_block" {
  bucket                  = aws_s3_bucket.tf_state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true # Crucial for preventing public access
}
```

#### `dynamo.tf`

This file sets up the DynamoDB table specifically for state locking.

```terraform
resource "aws_dynamodb_table" "tf_locks" {
  name         = var.dynamodb_name
  billing_mode = "PAY_PER_REQUEST" # Cost-effective for locking
  hash_key     = "LockID" # Required primary key for locking

  attribute {
    name = "LockID"
    type = "S" # String type for the LockID
  }

  tags = {
    Name = "Terraform State Lock Table"
  }
}
```

`
`

**Deployment Steps for Backend Infrastructure:**

1.  **Save these files:** Place `main.tf`, `variables.tf`, `s3.tf`, and `dynamo.tf` into your dedicated temporary directory (e.g., `terraform-backend-setup`).
2.  **Initialize Terraform:** Navigate to this directory in your terminal and run `terraform init`.
3.  **Plan and Apply:** Run `terraform plan` to see what will be created, and then `terraform apply`. When prompted, provide a **globally unique name** for your S3 bucket. For example: `bucket_name = "my-terraform-states-12345"`. You can accept the default for `dynamodb_name` if you like.
    - **A quick but crucial tip:** Your S3 bucket name _must_ be globally unique across all of AWS. Otherwise, AWS will give you a friendly little error!

Once your S3 bucket and DynamoDB table are successfully provisioned, you won't need that temporary directory anymore, so feel free to give it the ol' delete if you wish!

### Integrating into Your Project

Now, here's where the magic happens for your actual Terraform projects. You'll add a `backend` block to your project's configuration, but with a twist!

**Security Best Practice Alert!** It's generally a bad idea to hardcode your bucket and DynamoDB table names directly into your main project's `backend` block. Why? Security and flexibility! We'll define these during the `terraform init` command instead.

Add this minimal `backend` block to your project's main Terraform configuration (e.g., in your `main.tf` file or a dedicated `backend.tf`):

```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket-uniq-example"
    key            = "terraform.tfstate"
    region         = "eu-west-1"
    dynamodb_table = "terraform-locks-example"
    encrypt        = true
  }
}
```

And then, when you run `terraform init` for your actual project, you'll pass in the backend configuration like so:

```bash
terraform init -backend-config="bucket=your_globally_unique_s3_bucket_name" -backend-config="dynamodb_table=terraform-locks"
```

Just replace `your_globally_unique_s3_bucket_name` with the actual name of the S3 bucket you created earlier. Use the `dynamodb_name` you chose (or the default `terraform-locks`).

### And That's It!

From now on, whenever you run Terraform commands, your `tfstate` file will be pushed to your shiny new S3 bucket. Plus, Terraform automatically checks for updates on the `tfstate` file every single run, ensuring everything stays in sync and locked down.

Thanks for reading, and happy Terraforming!
