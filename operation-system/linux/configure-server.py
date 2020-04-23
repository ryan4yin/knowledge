#!/usr/bin/python3

"""
为 ubuntu 18.04 主机设置 ip，hostname, 设置 sysctl 参数、limits 参数

需要以 root 身份运行
"""

import re
import os
import sys
import shlex
import subprocess
from pathlib import Path

# pyyaml，ubuntu 自带
import yaml

os_name = "ubuntu"
default_nameservers = '192.168.1.2'  # 内网 dns 服务器，逗号分隔

cloud_cfg_path = Path("/etc/cloud/cloud.cfg")  # 设置 hostname 前，需要修改这个文件
netplan_cfg_path = Path("/etc/netplan/50-cloud-init.yaml")  # netplan 网卡配置文件

netplan_cfg = yaml.safe_load(netplan_cfg_path.read_bytes())

# sysctl 和 limits 参数设置
sysctl_cfg_path = Path("/etc/sysctl.conf")
limits_cfg_path = Path("/etc/security/limits.conf")

sysctl_custom_cfg = """
#同时可以拥有的的异步IO请求数目。
fs.aio-max-nr = 104857
#系统所有进程一共可以打开的文件数量
fs.file-max = 655356

# elasticsearch 6.8+ 需要设置以下参数
# 非 es 不要启用这个参数，否则可能会出问题。
# vm.max_map_count=262144

# 增大最大连接数
net.core.somaxconn = 50000
# 只要还有内存的情况下，就不使用 swap 交换空间
vm.swappiness = 0
"""

limits_custom_cfg = """
*       soft    nproc   65535
*       hard    nproc   65535
root    soft    nproc   65535
root    hard    nproc   65535

*       soft    nofile  655350
*       hard    nofile  655350
root    soft    nofile  655350
root    hard    nofile  655350
"""


def get_eth_name():
    """获取网卡名称，如果有多个网卡，让用户自己选择"""
    eth_dict = netplan_cfg['network']['ethernets']
    len_eth_list = len(eth_dict)
    if len_eth_list == 1:
        eth_name = list(eth_dict)[0]
    elif len_eth_list > 1:
        print(f"multiple ethernets found: {list(eth_dict.keys())}")
        eth_name = input("input the ethernet name you want to configure: ")
    else:
        print("Error! no ethernets found!")
        sys.exit(-1)

    return eth_name


def set_static_ip(eth_name, static_ip, gateway4, nameservers):
    """通过 netplan 设置静态 ip"""
    # 修改 netplan 配置
    eth_dict = netplan_cfg['network']['ethernets']
    eth_dict[eth_name] = {
        "dhcp4": False,
        'addresses': [f'{static_ip}/24'],
        'gateway4': gateway4,
        'nameservers': {
            'addresses': nameservers.replace(" ", "").split(",")
        }
    }

    netplan_cfg_text = yaml.safe_dump(netplan_cfg, allow_unicode=True)
    # 使用 netplan apply 命令应用配置
    netplan_cfg_path.write_text(netplan_cfg_text, encoding="utf-8")
    subprocess.run("netplan apply && reboot", shell=True)


def set_hostname(hostname: str):
    """修改主机名称"""
    # 1. 修改 cloud_cfg，否则对 hostname 的修改无法生效
    cloud_cfg = cloud_cfg_path.read_text(encoding="utf-8")
    cloud_cfg = re.sub(r"preserve_hostname: +true",
                       r"preserve_hostname: false", cloud_cfg)
    cloud_cfg_path.write_text(cloud_cfg, encoding="utf-8")

    # 检查 hostname 是否合法
    if not re.fullmatch(r"[a-zA-Z0-9\-]+", hostname):
        print("hostname can only contains digits, letters and '-'")
        sys.exit(-1)

    Path("/etc/hostname").write_text(hostname, encoding="utf-8")


def set_limits_and_sysctl():
    """优化系统的 limits 和 sysctl 参数"""
    for p, custom_cfg in {
        limits_cfg_path: limits_custom_cfg,
        sysctl_cfg_path: sysctl_custom_cfg
    }.items():
        cfg_text = p.read_text()
        if custom_cfg in cfg_text:
            print(f"{p.as_posix()} has been configured, skip it")
        else:
            print(f"add cfg to {p.as_posix()}:\n{custom_cfg}")
            p.write_text("\n".join(
                (cfg_text, custom_cfg)
            ), encoding="utf-8")
        
        print("-"*30)


def main():
    # 1. 设置 limits.conf 和 sysctl.conf
    if input("configure limits.conf and sysctl.conf? (y/n)") not in ('y', 'yes'):
        return
    
    set_limits_and_sysctl()
    print("need reboot after configured")

    # 2. 选择网卡
    print("-"*30)
    eth_name = get_eth_name()
    print(f"start to configure ethernet: {eth_name}")

    # 3. 其他参数
    static_ip = input("set staic ip: ")
    if not re.fullmatch(r"\d+(\.\d+){3}", static_ip):
        print("请输入正确的 ip 地址（ipv4）！")
        return

    default_gateway4 = static_ip.rsplit(".", maxsplit=1)[0] + ".1"
    gateway4 = input(f"set gateway4(default: {default_gateway4}): ") or default_gateway4
    nameservers = input(
        f"nameservers(dns servers), separated by commas(default: {default_nameservers}):") or default_nameservers

    role = input(
        "the role of this host(eg. k8s-node, k8s-master, nginx, gitlab...): ")
    hostname = "-".join((role, os_name, static_ip.replace(".", "-")))

    # 再次确认参数
    print("-"*30)
    for k, v in {
        "ethernet": eth_name,
        "static_ip": static_ip,
        "gateway4": gateway4,
        "nameservers": nameservers,
        "hostname": hostname
    }.items():
        print(f"{k}: {v}")

    if input("configure this server and reboot?(y/n)") not in ('y', 'yes'):
        return

    # 修改系统配置
    set_hostname(hostname)
    set_static_ip(eth_name, static_ip, gateway4, nameservers)


if __name__ == "__main__":
    main()