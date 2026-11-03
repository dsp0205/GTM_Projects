with as_of as (select date_trunc('month', max(created_at)) as m from opportunities),
size as (select cohort, count(*) as n from account_funnel group by 1),
hits as (
  select f.cohort, date_diff('month', f.cohort, date_trunc('month', o.created_at)) as k, count(*) as c
  from account_funnel f join opportunities o using (account_id)
  group by 1, 2),
grid as (
  select s.cohort, s.n, k
  from size s, range(0, 7) as r(k), as_of
  where s.cohort + to_months(k) <= as_of.m)
select g.cohort::date as cohort, g.n, g.k as months_since,
       round(100.0 * sum(coalesce(h.c, 0)) over (partition by g.cohort order by g.k) / g.n, 1) as pct_with_opp
from grid g left join hits h on h.cohort = g.cohort and h.k = g.k
order by 1, 3;
