# eSIM 虚拟卡

eSIM 是一种嵌入到设备中的可编程 SIM 卡，它类似 NFC，可以通过编程模拟成各种 SIM 卡进行使用，无需实体卡。

主要用途：

- 穿戴设备：如智能手表通常都内置了 eSIM，只需开通运营商的 eSIM 服务，即可使用手机直接上网通话。
- 旅游出行：无需插入实体卡，扫一个二维码即可完成 eSIM 卡的安装激活，直接上网。
  - 国内的主流 Android 手机系统基本都自带了「国际上网」功能，也可直接在该平台上购买国际流量套餐，到了目的地可离线激活使用。
- 国际手机号：因为旅游或商务需求，很多人会需要一些其他国家的手机号用于各 APP 注册、电话短信等，而 eSIM 可直接网上购买，扫码安装，非常方便。

缺点：

- 手机出售或处置时，必须删除或转移 eSIM 账户。
- 物理设备丢失时 eSIM 账户的找回可能是个麻烦。

## eSIM Adapter / eSIM 存储卡 / eSIM 实体卡

eSIM
Adapter 是一张实体卡形式的 eSIM 存储卡，在 Android 上它通常和厂商开发的 APP 配套使用，通常一张 eSIM 可存储十多张 eSIM 卡，并且可通过 APP 很简单的在这些卡之间切换使用。

由于政策原因，所有中国大陆国行版手机自带的 eSIM 都是阉割了的，存在各种限制：

- 绝大部分国行手机的 eSIM 只能通过它自带的「国际上网」功能使用，需要开启定位才能激活 eSIM，只能用于上网而且价格较贵。
- Apple 的 eSIM 在国内只能激活国内的 eSIM Profile，在境外则需要开启定位才能激活境外的 eSIM Profile.

插入一张 eSIM Adapter 就可以绕过这些限制。

要购买 eSIM Adapter，有如下几种选择：

- 省心版：planbesim.com / xesim.cc / 9eSIM
- 技术党：淘宝购买 eUICC 读卡器 + eUICC 白卡，通过读卡器刷入 eSIM Profile

> NOTE: 由于缺失 China Certificate Issuer (CI) 和 GSMA Test CI，目前所有品牌发行的 eUICC 卡片均不能写入中国大陆运营商的 eSIM Profile。

## 获取 eSIM Profile

往 eSIM 卡中刷入不同的 eSIM Profile，它就能变成不同的 SIM 卡。
如前所述，这一操作可以通过 eGICC 读卡器完成，也可以通过一些厂家提供的安卓 APP 完成。

eSIM Profile 商家：

- 纯流量套餐
  - Klook / Trip 等 APP 上搜索购买
  - 红茶移动：<https://esim.redteago.com/zh-CN>
  - <https://esimdb.com>
  - <https://esims.io>
- 保号套餐（主要用于当地 APP 注册、短信电话接收，具体攻略建议小红书搜索）
  - 英国
    - giffgaff: <https://www.giffgaff.com/blog/giffgaff-news/how-to-get-a-giffgaff-esim/>
    - three hk: <https://www.three.co.uk/>
  - 美国
    - Helium: <https://heliummobile.com/>
    - Tello


## 参考文档

- [eSIM 转 SIM 实体卡](https://iecho.cc/2023/10/20/convert-esim-to-physical-sim/)

