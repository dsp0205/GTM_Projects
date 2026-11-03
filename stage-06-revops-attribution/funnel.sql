create or replace view account_funnel as
select a.account_id,
       date_trunc('month', a.first_seen) as cohort,
       exists (select 1 from touches t where t.account_id = a.account_id) as engaged,
       o.opp_id is not null as has_opp,
       coalesce(o.stage = 'won', false) as won
from (select account_id, min(created_at) as first_seen from contacts group by 1) a
left join opportunities o on o.account_id = a.account_id;

with s as (
  select count(*) as known,
         count(*) filter (where engaged) as engaged,
         count(*) filter (where has_opp) as opp,
         count(*) filter (where won)     as won
  from account_funnel)
select stage, accounts,
       round(100.0 * accounts / lag(accounts) over (order by ord), 1) as step_conv_pct,
       round(100.0 - 100.0 * accounts / lag(accounts) over (order by ord), 1) as leaked_pct
from (select 1 as ord, 'known account' as stage, known as accounts from s
      union all select 2, 'engaged', engaged from s
      union all select 3, 'opportunity', opp from s
      union all select 4, 'closed-won', won from s)
order by ord;
