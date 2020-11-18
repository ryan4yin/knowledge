terraform {
  required_providers {
    acme = {
      source = "terraform-providers/acme"
    }
  }
  required_version = ">= 0.13"
}


# 通过环境变量传入 ALICLOUD_ACCESS_KEY / ALICLOUD_SECRET_KEY
provider "alicloud" {
  region = "cn-shenzhen"
}

provider "acme" {
  server_url = "https://acme-staging-v02.api.letsencrypt.org/directory"
}

# TLS 证书私钥使用 ECC 算法
resource "tls_private_key" "private_key" {
  algorithm   = "ECDSA"
  ecdsa_curve = "P384"
}

# 组织身份信息
resource "acme_registration" "reg" {
  account_key_pem = tls_private_key.private_key.private_key_pem
  email_address   = "nobody@example.com"
}

# 创建证书/更新证书
resource "acme_certificate" "certificate" {
  account_key_pem           = acme_registration.reg.account_key_pem
  common_name               = "example.com"
  subject_alternative_names = ["*.example.com"]

  dns_challenge {
    provider = "alidns"
  }
}


# 将新证书上传到阿里云
resource "alicloud_cas_certificate" "alicloud-test-cert" {
  name = "test-cert"
  cert = acme_certificate.certificate.certificate_pem
  key  = acme_certificate.certificate.private_key_pem
}

