# Flow Log 数据分析

分析 NAT 网关的流日志，确定流量大的内外网 IP 地址，反查对应的公网域名、内网服务，再考虑优化手段：

```sql
SELECT
  interface_id,
  srcaddr,
  dstaddr,
  sum(bytes) as bytes
FROM vpc_flow_logs_xxx
WHERE
  year = '2022'
  AND month = '06'
  AND day = '24'
  AND hour = '09'
  and "action" = 'ACCEPT'
  and interface_id = 'xxx'
group by 1,2,3
order by
  4 DESC
```

## 基于 CIDR 地址块进行数据分析

首先，可启用 vpc_id subnet_id az_id 三个参数，它们均可用于分析 srcaddr 的子网、可用区信息。

比如分析某可用区（子网）的跨区流量，确定此可用区的跨区流量成本：

```sql
SELECT
  srcaddr,
  dstaddr,
  az_id,
  sum(bytes) as bytes
FROM vpc_flow_logs_ecs_vpc
WHERE
  year = '2022'
  AND month = '06'
  AND day = '24'
  and regexp_extract(dstaddr, '^......') = 'xxx.xxx'  -- 目的地是当前 VPC xxx.xxx.0.0/16，即 VPC 内部流量
```

但是如果子网的 CIDR 掩码不是 8 的倍数的话，上面这种前缀匹配的方法就失效了。这种场景下，AWS 官方博客
介绍了一个笨办法，先用脚本生成出 CIDR 地址块与所有 IP 地址的对照关系表存为 csv，然后再将它上传到 S3
导入到 Athena 中使用。

首先使用 Python 脚本穷举 IP 地址：

```python
from pathlib import Path
import ipaddress
import csv

def to_csv(fieldnames: tuple, data_list: list, csv_path: Path):
    with csv_path.open('w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for row_dict in data_list:
            writer.writerow(row_dict)

def generate_csv_for_subnets(subnets, csv_path):
    fieldnames = ("ipaddr", "cidr_block")
    data_list = []
    for subnet in subnets:
        for ipaddr in subnet:
            row_dict = {"ipaddr": ipaddr, "cidr_block": subnet}
            data_list.append(row_dict)
    to_csv(fieldnames, data_list, csv_path)

def main():
    subnets = [
        # 所有子网的 CIDR 地址块
        ipaddress.ip_network('172.30.64.0/19'),
        ipaddress.ip_network('172.30.96.0/19'),
        ipaddress.ip_network('172.30.128.0/19'),
    ]
    csv_path = Path("./ipaddr_cidr.csv")
    generate_csv_for_subnets(subnets,csv_path)

main()
```

再上传到 S3 并创建对应的 Athena 表:

```sql
CREATE EXTERNAL TABLE default.vpc_ipaddr_cidr
    (
        `ipaddr` varchar,
        `cidr_block` varchar,
    )
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 's3://my_bucket/some_bucket/dat/'
TBLPROPERTIES ('skip.header.line.count'='1')
```

查询从某可用区发出的所有跨区流量：

```sql
SELECT
  az_id,
  sum(bytes) as bytes
FROM vpc_flow_logs_ecs_vpc
WHERE
  year = '2022'
  AND month = '06'
  AND day = '24'
  AND az_id = 'us-east-1a' -- 源地址在这个可用区
  -- dstaddr 不在当前可用区的任一子网，下面穷举下当前可用区的所有子网 CIDR
  AND (dstaddr not in (select ip from default.vpc_ipaddr_cidr where cidr_block='172.30.64.0/19'))
  AND (dstaddr not in (select ip from default.vpc_ipaddr_cidr where cidr_block='172.30.96.0/19'))
```

## 其他分析手段

- [Presto IP Functions](https://prestodb.io/docs/current/functions/ip.html) 提供了 IPPREFIX 跟
  IPADDRESS 两个类型以及相关的函数
- [Analyze Network Traffic of Amazon Virtual Private Cloud (VPC) by CIDR blocks](https://aws.amazon.com/cn/blogs/networking-and-content-delivery/analyze-network-traffic-of-amazon-virtual-private-cloud-vpc-by-cidr-blocks/)
