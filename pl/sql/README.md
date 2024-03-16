# SQL

按日期对比某两天的数据：

```sql
select
        c1.product,
        c1.region,
        round(c1.cost, 2) c1_cost,
        round(c2.cost, 2) c2_cost,
        round(c2.cost - c1.cost, 2) as cost_growth,
        round(100 * (c2.cost - c1.cost) / c1.cost, 1) as cost_growth_rate
from (
  (
    select
        product,
        region,
        sum(cost) as cost
    from `my_cost`
    where date_ = '2022-05-01'
    group by 1,2
  ) as c1
  left outer join (
    select
        product,
        region,
        sum(cost) as cost
    from `my_cost`
    where date_ = '2022-06-01'
    group by 1,2
  ) as c2
  on c1.product = c2.product
  and c1.region = c2.region
) where abs(c2.cost - c1.cost) > 20  -- 只查看差别较大的行
order by product, cost_growth desc
```
