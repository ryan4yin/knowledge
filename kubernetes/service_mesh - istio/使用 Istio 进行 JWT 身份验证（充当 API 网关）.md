>本文基于 Istio1.5 编写测试

Istio 支持使用 JWT 对终端用户进行身份验证（Istio End User Authentication），支持多种 JWT 签名算法。

目前主流的 JWT 算法是 RS256/ES256。（请忽略 HS256，该算法不适合分布式 JWT 验证）

这里以 RSA256 算法为例进行介绍，ES256 的配置方式也是一样的。

### 1. JWK 说明

要在 Istio 上使用 JWT 身份验证，就得先介绍一下 JWK。

JWK 全称是 Json Web Key，它描述了一个加密密钥（公钥或私钥）的各项属性，包括密钥的值。

Istio 使用 JWK 描述验证签名所需要的信息。在使用 RSA 签名算法时，JWK 描述的应该是用于验证的 RSA 公钥。

一个 RSA 公钥的 JWK 描述如下：

```
{
    "alg": "RS256",  # 算法「可选参数」
    "kty": "RSA",    # 密钥类型
    "use": "sig",    # 被用于签名「可选参数」
    "kid": "NjVBRjY5MDlCMUIwNzU4RTA2QzZFMDQ4QzQ2MDAyQjVDNjk1RTM2Qg",  # key id，在有多个 jwk 时(如 jwks 中)被用于区分各 jwk
    "n": "yeNlzlub94YgerT030codqEztjfU_S6X4DbDA_iVKkjAWtYfPHDzz_sPCT1Axz6isZdf3lHpq_gYX4Sz-cbe4rjmigxUxr-FgKHQy3HeCdK6hNq9ASQvMK9LBOpXDNn7mei6RZWom4wo3CMvvsY1w8tjtfLb-yQwJPltHxShZq5-ihC9irpLI9xEBTgG12q5lGIFPhTl_7inA1PFK97LuSLnTJzW0bj096v_TMDg7pOWm_zHtF53qbVsI0e3v5nmdKXdFf9BjIARRfVrbxVxiZHjU6zL6jY5QJdh1QCmENoejj_ytspMmGW7yMRxzUqgxcAqOBpVm0b-_mW3HoBdjQ",
    "e": "AQAB"
}
```

RSA 是基于大数分解的加密/签名算法，上述参数中，`e` 是公钥的模数(modulus)，`n` 是公钥的指数(exponent)，两个参数都是 base64 字符串。

JWK 中 RSA 公钥的具体定义参见 [RSA Keys - JSON Web Algorithms (JWA)](https://tools.ietf.org/html/rfc7518#page-30)

### 2. JWK 的生成

要生成 JWK 公钥，需要先生成私钥，生成方法参见 [JWT 签名算法 HS256、RS256 及 ES256 及密钥生成 ](https://www.cnblogs.com/kirito-c/p/12402066.html#228229456)。

>公钥不需要用上述方法生成，因为我们需要的是 JWK 格式的公钥。后面会通过 python 生成出 JWK 公钥。

上面的命令会将生成出的 RSA 私钥写入 key.pem 中，查看一下私钥内容。

```
ryan@RYAN-MI-DESKTOP:~/istio$ cat key.pem
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAt1cKkQqPh8iOv5BhKh7Rx6A2+1ldpO/jczML/0GBKu4X+lHr
Y8YbJrt29jyAXlWM8vHC7tXsqgUG+WziRD0D8nhnh10XC14SeH+3mVuBqph+TqhX
TWsh9gtAIbeUHJjEI4I79QK4/wquPHHIGZBQDQQnuMh6vAS3VaUYJdEIoKvUBnAy
Y35kJZgyJSbrxLsEExL2zujUD/OY+/In2bq/3rFtDGNlgHyC7Gu2zXSXvfOA4O5m
9BBXOc7eEqj7PoOKNaTxLN3YcuRtgR6NIXL4KLb6oyvIzoeiprt4+9q7sc3Dnkc5
EV9kwWlEW2DHzhP6VYca0WXIIXc53U1AM3ewxwIDAQABAoIBABIKhaaqJF+XM7zU
B0uuxrPfJynqrFVbqcUfQ9H1bzF7Rm7CeuhRiUBxeA5Y+8TMpFcPxT/dWzGL1xja
RxWx715/zKg8V9Uth6HF55o2r/bKlLtGw3iBz1C34LKwrul1eu+HlEDS6MNoGKco
BynE0qvFOedsCu/Pgv7xhQPLow60Ty1uM0AhbcPgi6yJ5ksRB1XjtEnW0t+c8yQS
nU3mU8k230SdMhf4Ifud/5TPLjmXdFpyPi9uYiVdJ5oWsmMWEvekXoBnHWDDF/eT
VkVMiTBorT4qn+Ax1VjHL2VOMO5ZbXEcpbIc3Uer7eZAaDQ0NPZK37IkIn9TiZ21
cqzgbCkCgYEA5enHZbD5JgfwSNWCaiNrcBhYjpCtvfbT82yGW+J4/Qe/H+bY/hmJ
RRTKf0kVPdRwZzq7GphVMWIuezbOk0aFGhk/SzIveW8QpLY0FV/5xFnGNjV9AuNc
xrmgVshUsyQvr1TFkbdkC6yuvNgQfXfnbEoaPsXYEMCii2zqdF5lWGUCgYEAzCR2
6g8vEQx0hdRS5d0zD2/9IRYNzfP5oK0+F3KHH2OuwlmQVIo7IhCiUgqserXNBDef
hj+GNcU8O/yXLomAXG7VG/cLWRrpY8d9bcRMrwb0/SkNr0yNrkqHiWQ/PvR+2MLk
viWFZTTp8YizPA+8pSC/oFd1jkZF0UhKVAREM7sCgYB5+mfxyczFopyW58ADM7uC
g0goixXCnTuiAEfgY+0wwXVjJYSme0HaxscQdOOyJA1ml0BBQeShCKgEcvVyKY3g
ZNixunR5hrVbzdcgKAVJaR/CDuq+J4ZHYKByqmJVkLND4EPZpWSM1Rb31eIZzw2W
5FG8UBbr/GfAdQ6GorY+CQKBgQCzWQHkBmz6VG/2t6AQ9LIMSP4hWEfOfh78q9dW
MDdIO4JomtkzfLIQ7n49B8WalShGITwUbLDTgrG1neeQahsMmg6+X99nbD5JfBTV
H9WjG8CWvb+ZF++NhUroSNtLyu+6LhdaeopkbQVvPwMArG62wDu6ebv8v/5MrG8o
uwrUSwKBgQCxV43ZqTRnEuDlF7jMN+2JZWhpbrucTG5INoMPOC0ZVatePszZjYm8
LrmqQZHer2nqtFpyslwgKMWgmVLJTH7sVf0hS9po0+iSYY/r8e/c85UdUreb0xyT
x8whrOnMMODCAqu4W/Rx1Lgf2vXIx0pZmlt8Df9i2AVg/ePR6jO3Nw==
-----END RSA PRIVATE KEY-----
```

接下来通过 Python 编程生成 RSA Public Key 和 JWK（jwk 其实就是公钥的另一个表述形式而已）:

```
# 需要先安装依赖: pip install jwcrypto
from jwcrypto.jwk import JWK
from pathlib import Path

private_key = Path("key.pem").read_bytes()
jwk = JWK.from_pem(private_key)

# 导出公钥 RSA Public Key
public_key = jwk.public().export_to_pem()
print(public_key)

print("="*30)

# 导出 JWK
jwk_bytes = jwk.public().export()
print(jwk_bytes)
```

Istio 需要 JWK 进行 JWT 验证，而我们手动验证 JWT 时一般需要用到 Public Key. 方便起见，上述代码把这两个都打印了出来。内容如下：

```
# Public Key 内容，不包含这行注释
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAt1cKkQqPh8iOv5BhKh7R
x6A2+1ldpO/jczML/0GBKu4X+lHrY8YbJrt29jyAXlWM8vHC7tXsqgUG+WziRD0D
8nhnh10XC14SeH+3mVuBqph+TqhXTWsh9gtAIbeUHJjEI4I79QK4/wquPHHIGZBQ
DQQnuMh6vAS3VaUYJdEIoKvUBnAyY35kJZgyJSbrxLsEExL2zujUD/OY+/In2bq/
3rFtDGNlgHyC7Gu2zXSXvfOA4O5m9BBXOc7eEqj7PoOKNaTxLN3YcuRtgR6NIXL4
KLb6oyvIzoeiprt4+9q7sc3Dnkc5EV9kwWlEW2DHzhP6VYca0WXIIXc53U1AM3ew
xwIDAQAB
-----END PUBLIC KEY-----
```

```
# jwk 内容
{
 'e': 'AQAB',
 'kid': 'oyYwZSLCLVVPHdVp0jXIcLNpGn6dMCumlY-6wSenmFo',
 'kty': 'RSA',
 'n': 't1cKkQqPh8iOv5BhKh7Rx6A2-1ldpO_jczML_0GBKu4X-lHrY8YbJrt29jyAXlWM8vHC7tXsqgUG-WziRD0D8nhnh10XC14SeH-3mVuBqph-TqhXTWsh9gtAIbeUHJjEI4I79QK4_wquPHHIGZBQDQQnuMh6vAS3VaUYJdEIoKvUBnAyY35kJZgyJSbrxLsEExL2zujUD_OY-_In2bq_3rFtDGNlgHyC7Gu2zXSXvfOA4O5m9BBXOc7eEqj7PoOKNaTxLN3YcuRtgR6NIXL4KLb6oyvIzoeiprt4-9q7sc3Dnkc5EV9kwWlEW2DHzhP6VYca0WXIIXc53U1AM3ewxw'
}
```

### 3. JWK Set 说明

JWK Set，也就是 JWK 集合，是一个 json 数据结构：

```
{
"keys": [
  {<jwk-1>},
  {<jwk-2>},
  ...
]}
```

非常简单的结构。JWKS 主要用于密钥的 Rotate，因为它能同时描述多个可用的公钥。

### 4. 测试密钥可用性

接下来在 [jwt.io](https://jwt.io) 中填入测试用的公钥私钥，还有 Header/Payload。一是测试公私钥的可用性，二是生成出 JWT 供后续测试 Istio JWT 验证功能的可用性。
![](https://img2020.cnblogs.com/blog/968138/202003/968138-20200313182424322-30548475.png)

可以看到左下角显示「Signature Verified」，成功地生成出了 JWT。后续可以使用这个 JWT 访问 Istio 网关，测试 Istio JWT 验证功能。

### 5. 启用 Istio 的身份验证

编写 istio 配置：

```yaml
apiVersion: "security.istio.io/v1beta1"
kind: "RequestAuthentication"
metadata:
  name: "jwt-example"
  namespace: istio-system  # istio-system 名字空间中的配置，默认情况下会应用到所有名字空间
spec:
  selector:
    matchLabels:
      istio: ingressgateway
  jwtRules:
  - issuer: "testing@secure.istio.io"
    jwks: |
    {
        "keys": [
            {
                "e": "AQAB",
                "kid": "oyYwZSLCLVVPHdVp0jXIcLNpGn6dMCumlY-6wSenmFo",
                "kty": "RSA",
                "n": "t1cKkQqPh8iOv5BhKh7Rx6A2-1ldpO_jczML_0GBKu4X-lHrY8YbJrt29jyAXlWM8vHC7tXsqgUG-WziRD0D8nhnh10XC14SeH-3mVuBqph-TqhXTWsh9gtAIbeUHJjEI4I79QK4_wquPHHIGZBQDQQnuMh6vAS3VaUYJdEIoKvUBnAyY35kJZgyJSbrxLsEExL2zujUD_OY-_In2bq_3rFtDGNlgHyC7Gu2zXSXvfOA4O5m9BBXOc7eEqj7PoOKNaTxLN3YcuRtgR6NIXL4KLb6oyvIzoeiprt4-9q7sc3Dnkc5EV9kwWlEW2DHzhP6VYca0WXIIXc53U1AM3ewxw"
            }
        ]
    }
      # jwks 或 jwksUri 二选其一
      # jwksUri: "http://nginx.test.local/istio/jwks.json"
```

现在 `kubectl apply` 一下，JWT 验证就添加到全局了。

可以看到 jwtRules 是一个列表，因此可以为每个 issuers 配置不同的 jwtRule.

对同一个 issuers（jwt 签发者），可以通过 jwks 设置多个公钥，以实现JWT签名密钥的轮转。
JWT 的验证规则是：

1. JWT 的 payload 中有 issuer 属性，首先通过 issuer 匹配到对应的 istio 中配置的 jwks。
2. JWT 的 header 中有 kid 属性，第二步在 jwks 中找到 kid 相同的公钥。
3. 使用找到的公钥进行 JWT 签名验证。


### 6. 启用 Payload 转发/Authorization 转发

默认情况下，Istio 在完成了身份验证之后，会去掉 Authorization 请求头再进行转发。
这将导致我们的后端服务获取不到对应的 Payload，无法判断 End User 的身份。
因此我们需要启用 Istio 的 Authorization 请求头的转发功能，在前述的 `RequestAuthentication` yaml 配置中添加一个参数就行：

```yaml
apiVersion: "security.istio.io/v1beta1"
kind: "RequestAuthentication"
metadata:
  name: "jwt-example"
  namespace: istio-system
spec:
  selector:
    matchLabels:
      istio: ingressgateway
  jwtRules:
  - issuer: "testing@secure.istio.io"
    jwks: |
    {
        "keys": [
            {
                "e": "AQAB",
                "kid": "oyYwZSLCLVVPHdVp0jXIcLNpGn6dMCumlY-6wSenmFo",
                "kty": "RSA",
                "n": "t1cKkQqPh8iOv5BhKh7Rx6A2-1ldpO_jczML_0GBKu4X-lHrY8YbJrt29jyAXlWM8vHC7tXsqgUG-WziRD0D8nhnh10XC14SeH-3mVuBqph-TqhXTWsh9gtAIbeUHJjEI4I79QK4_wquPHHIGZBQDQQnuMh6vAS3VaUYJdEIoKvUBnAyY35kJZgyJSbrxLsEExL2zujUD_OY-_In2bq_3rFtDGNlgHyC7Gu2zXSXvfOA4O5m9BBXOc7eEqj7PoOKNaTxLN3YcuRtgR6NIXL4KLb6oyvIzoeiprt4-9q7sc3Dnkc5EV9kwWlEW2DHzhP6VYca0WXIIXc53U1AM3ewxw"
            }
        ]
    }
# ===================== 添加如下参数===========================
    forwardOriginalToken: true  # 转发 Authorization 请求头
```

加了转发后，流程图如下（需要 mermaid 渲染）：

```mermaid
sequenceDiagram
autonumber
participant User as 用户
participant Auth as 授权服务
participant IG as IngressGateway
participant SVC as 某服务
User->>+Auth: Login
Auth-->>-User: 返回 JWT
User->>+IG: 请求信息（带 JWT）
IG->>-SVC: 请求信息（转发 JWT）
SVC-->>IG: 返回信息
IG-->>User: 返回信息
```

## 其他

Istio 的 JWT 验证规则，默认情况下会直接忽略不带 Authorization 请求头的流量，因此这类流量能直接进入网格内部。如果需要禁止不带 Authorization 头的流量，需要额外配置 AuthorizationPolicy 策略。

RequestsAuthentication 验证失败的请求，Istio 会返回 401 状态码。
AuthorizationPolicy 验证失败的请求，Istio 会返回 403 状态码。

这会导致在使用 AuthorizationPolicy 禁止了不带 Authorization 头的流量后，这类请求会直接被返回 403。。。在使用 RESTful API 时，这种情况可能会造成一定的问题。

## 参考

- [JSON Web Key Set Properties - Auth0](https://auth0.com/docs/tokens/references/jwks-properties)
- [JWK - RFC7517](https://tools.ietf.org/html/rfc7517)
- [Sample JWT and JWKS data for demo - Istio Security](https://github.com/istio/istio/tree/master/security/tools/jwt/samples)
- [End User Authentication - Istio](https://istio.io/docs/tasks/security/authentication/authn-policy/#end-user-authentication)
- [JWTRule - Istio](https://istio.io/docs/reference/config/security/jwt/)
- [jwt.io - 动态生成 jwt](https://jwt.io/)