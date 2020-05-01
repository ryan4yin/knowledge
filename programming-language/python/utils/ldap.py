import json

from ldap3 import Server, Connection, ALL, NTLM


"""
ldap 相关，只在 Windows AD 域提供的 LDAP 上测试过
"""

class Ldap:
    user_attrs = [  # ad 域对大小写不敏感
        "mail",
        "mobile",  # 对应用户信息「电话」页中的「移动电话」！
        "telephoneNumber",  # 对应用户信息首页的「电话号码」
        "displayName"
    ]  # 用户的几个用得到的属性

    def __init__(self,
                 user: str,  # 管理员账户
                 password: str,
                 server_url: str,  # Windows域控地址
                 ):
        self.server = Server(server_url, get_info=ALL)
        self.conn = Connection(
            self.server,
            user=f"AD\\{user}",  # 这里限定了 AD 域
            password=password,
            authentication=NTLM,
            auto_bind=True
        )

    def get_user_info(self, sAMAccountName: str, zone: str):
        """通过域用户的名称，获取到用户的其他信息

        :param sAMAccountName: Windows AD 域用户的账号名
        :param zone: 查找域，如 'ou=DevOps,dc=ad,dc=local'，ad.local 域中的 DevOps 组
        :return:
            {
                "displayName": "xxx",
                "mail": xxx,
                "mobile": xxx  # TelephoneNumber/Mobile 两个 AD 域属性之一。优先查看 TelephoneNumber
            }
        """
        if not self.conn.search(
            zone,
            f'(sAMAccountName={sAMAccountName})',  # sAMAccountName 是用户名
            attributes=self.user_attrs
        ):
            return

        user = json.loads(
            self.conn.entries[0].entry_to_json()
        )['attributes']
        for k, v in user.items():
            if not len(v):
                user[k] = None
            else:
                user[k] = v[0]

        # 如果存在 TelephoneNumber，优先使用它做为 Mobile 属性
        # 这是为了方便使用，我只需要知道用户的手机号，不想知道它的手机号被填在了哪。
        if user['telephoneNumber'] is not None:
            user['mobile'] = user['telephoneNumber']
        del user['telephoneNumber']

        return user
