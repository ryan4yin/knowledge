# Vault 基础概念


首先看一下 Vault 的架构图：

![vault layers](_imgs/vault-layers.png)

可以看到，几乎所有的组件都从属于「安全屏障(security barrier)」，
Vault 可以简单地被划分为 Storage Backend、安全屏障(security barrier) 和 Http API 三个部分。

「安全屏障(security barrier)」是 Vault(金库) 周围的加密「钢铁」和「混凝土」，Storage Backend 和 Vault 之间的所有数据流动都需要经过「屏障(barrier)」。
barrier 确保只有加密数据会被写入 Storage Backend，加密数据在经过 barrier 的过程中被验证与解密。
和银行金库(bank vault)非常类似，barrier 也必须先解封，才能允许读取内部的数据。

## 一、数据存储及加密解密

Storage Backend(后端存储): Vault 自身不存储数据，因此需要为它配置一个「Storage Backend」。
「Storage Backend」是不受信任的，只用于存储加密数据。

Initialaztion(初始化): vault 在首次启动时需要初始化，这一步生成一个「加密密钥(encryption key)」用于加密数据，加密完成的数据才能被保存到 Storage Backend.

Unseal(解封): Vault 启动后，因为不知道「加密密钥(encryption key)」，它会进入「封印(sealed)」状态，在「Unseal」前无法进行任何操作。
「加密密钥」被「master key」保护，我们必须提供「master key」才能完成 Unseal 操作。
默认情况下，vault 使用[沙米尔密钥共享算法](https://medium.com/taipei-ethereum-meetup/%E7%A7%81%E9%91%B0%E5%88%86%E5%89%B2-shamirs-secret-sharing-7a70c8abf664)
将「master key」分割成五个「Key Shares(分享密钥)」，必须要提供其中任意三个「Key Shares」才能重建出「master key」从而完成 Unseal.

![vault-shamir-secret-sharing](_imgs/vault-shamir-secret-sharing.svg)

>「Key Shares」的数量，以及重建「master key」最少需要的 key shares 数量，都是可以调整的。
沙米尔密钥共享算法也可以关闭，这样 master key 将被直接用于 Unseal.


## 二、认证系统及权限系统

在解封完成后，Vault 就可以开始处理请求了。

HTTP 请求进入后的整个处理流程都由 vault core 管理，core 会强制进行 ACL 检查，并确保审计日志(audit logging)完成记录。

客户端首次连接 vault 时，需要先完成身份认证，vault 的「auth methods」模块有很多身份认证方法可选：

1. 用户友好的认证方法，适合管理员使用：username/password、云服务商、ldap
2. 应用友好的方法：public/private keys、tokens、kubernetes、jwt

身份验证请求流经 Core 并进入 auth methods，auth methods 确定请求是否有效并返回「关联策略(policies)」的列表。

ACL Policies 由 policy store 负责管理与存储，由 core 进行 ACL 检查。
ACL 的默认行为是拒绝，这意味着除非明确配置 Policy 允许某项操作，否则该操作将被拒绝。

在通过 auth methods 完成了身份认证，并且返回的「关联策略」也没毛病之后，「token store」将会生成并管理一个新的 token，
这个 token 会被返回给客户端，用于进行后续请求。
类似 web 网站的 cookie，token 也都存在一个 lease 租期或者说有效期，这加强了安全性。

token 关联了相关的策略 policies，策略将被用于验证请求的权限。
请求经过验证后，将被路由到 secret engine。如果 secret engine 返回了一个 secret（由 vault 自动生成的 secret），
Core 会将其注册到 expiration manager，并给它附加一个 lease ID。lease ID 被客户端用于更新(renew)或吊销(revoke)它得到的 secret.
如果客户端允许租约(lease)到期，expiration manager 将自动吊销这个 secret.

Core 负责处理审核代理(audit brok)的请求及响应日志，将请求发送到所有已配置的审核设备(audit devices)。

