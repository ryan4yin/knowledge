# [Vault](https://github.com/hashicorp/vault)

Vault 和 Apollo 相比，最大的特点是它对敏感信息的支持非常完善。
它不仅支持保存各种自定义信息、自动生成各类密钥，还支持接入各大云厂商的账号权限体系，支持各种敏感信息的自动轮转，非常方便。

## 部署 Vault

官方建议[通过 Helm 部署 vault](https://www.vaultproject.io/docs/platform/k8s/helm/run)，大概流程：

1. 在 `custom-vaults.yaml` 中添加自定义的 vault 配置，通过 helm 部署。
2. 初始化/解封 vault: vault 安全措施，每次重启必须解封。

以 mysql 为后端存储的 HA 高可用 vault 的 `custom-vault.yaml` 内容大概如下：

```yaml

```

## 升级

待续
