# [Vault](https://github.com/hashicorp/vault)

Vault 和 Apollo 相比，最大的特点是它对敏感信息的支持非常完善：

1. 支持保存各种自定义信息、自动生成各类密钥，vault 自动生成的密钥还能自动轮转(rotate)
2. 支持接入各大云厂商的账号权限体系（比如阿里云RAM子账号），实现 APIKey/APISecret 的自动轮转。
3. 支持接入 kubernetes rbac 权限体系，通过 serviceaccount+role 为每个 Pod 单独配置权限。

## 部署 Vault

官方建议[通过 Helm 部署 vault](https://www.vaultproject.io/docs/platform/k8s/helm/run)，大概流程：

1. 在 `custom-vaults.yaml` 中添加自定义的 vault 配置，通过 helm 部署。
2. 初始化/解封 vault: vault 安全措施，每次重启必须解封。

以 mysql 为后端存储的 HA 高可用 vault 的 `custom-vault.yaml` 内容大概如下：

```yaml
server:
  ha:
    enabled: true
    config: |
      ui = true

      listener "tcp" {
        tls_disable = 1
        address = "[::]:8200"
        cluster_address = "[::]:8201"
      }

      storage "mysql" {
        address = "<host>:3306"
        username = "<username>"
        password = "<password>"
        database = "vault"
        ha_enabled = "true"
      }

      service_registration "kubernetes" {}


ui:
  enabled: true
```

通过 helm 部署：

```
# 添加 valut 仓库
helm repo add hashicorp https://helm.releases.hashicorp.com
# 查看 vault 版本号
helm search repo hashicorp/vault -l
# 下载某个版本号的 vault
helm pull hashicorp/vault --version 0.6.0 --untar
# 安装/升级 valut
helm upgrade vault ./vault --namespace vault -f custom-values.yaml
```




## 升级

待续
