create or replace view paths as
select o.opp_id, o.amount, coalesce(t.channel, 'no_touch') as channel, t.touch_ts,
       row_number() over w as pos,
       count(*) over (partition by o.opp_id) as n,
       coalesce(date_diff('day', t.touch_ts, o.created_at), 0) as days_before
from opportunities o
left join touches t
  on t.account_id = o.account_id
 and t.touch_ts <= o.created_at
 and t.touch_ts >  o.created_at - interval 180 day
where o.stage = 'won'
window w as (partition by o.opp_id order by t.touch_ts, t.touch_id);

create or replace view credit as
select *,
  (pos = 1)::int                                             as w_first,
  (pos = n)::int                                             as w_last,
  1.0 / n                                                    as w_linear,
  case when n = 1 then 1.0
       when n = 2 then 0.5
       when pos in (1, n) then 0.4
       else 0.2 / (n - 2) end                                as w_u_shaped,
  power(0.5, days_before / 7.0)
    / sum(power(0.5, days_before / 7.0)) over (partition by opp_id) as w_time_decay
from paths;

select channel,
  round(sum(amount * w_first))       as first_touch,
  round(sum(amount * w_last))        as last_touch,
  round(sum(amount * w_linear))      as linear,
  round(sum(amount * w_u_shaped))    as u_shaped,
  round(sum(amount * w_time_decay))  as time_decay
from credit
group by channel
order by channel;
