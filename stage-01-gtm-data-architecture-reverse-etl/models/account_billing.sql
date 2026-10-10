/* One row per Stripe customer. This file is the single definition of MRR. */
create or replace table account_billing as
with free_mail(domain) as (
    values ('gmail.com'), ('yahoo.com'), ('outlook.com'), ('hotmail.com'), ('icloud.com'), ('proton.me')
),
customers as (
    select
        payload->>'$.id'                          as stripe_customer_id,
        lower(payload->>'$.email')                as email,
        payload->>'$.name'                        as customer_name,
        lower(split_part(payload->>'$.email', '@', 2)) as email_domain
    from raw_stripe_customers
),
sub_items as (
    select
        payload->>'$.customer' as stripe_customer_id,
        payload->>'$.status'   as status,
        item
    from raw_stripe_subscriptions,
         unnest(cast(payload->'$.items.data' as json[])) as t(item)
),
mrr as (
    select
        stripe_customer_id,
        /* Rule: active and past_due count toward MRR. trialing and canceled do not. */
        cast(round(sum(case when status in ('active', 'past_due') then
              cast(item->>'$.price.unit_amount' as bigint)
              * coalesce(cast(item->>'$.quantity' as bigint), 1)
              / (case item->>'$.price.recurring.interval'
                     when 'year' then 12 when 'month' then 1 else null end
                 * coalesce(cast(item->>'$.price.recurring.interval_count' as bigint), 1))
            else 0 end)) as bigint)               as mrr_cents,
        max(status)                               as subscription_status
    from sub_items
    group by 1
),
usage as (
    select
        lower(split_part(user_email, '@', 2))     as email_domain,
        count(distinct user_email) filter (where occurred_at >= now() - interval 30 day) as active_users_30d,
        max(occurred_at)                          as last_event_at
    from raw_usage_events
    group by 1
)
select
    c.stripe_customer_id,
    c.customer_name,
    case when c.email_domain in (select domain from free_mail) then null else c.email_domain end as company_domain,
    coalesce(m.mrr_cents, 0)                      as mrr_cents,
    coalesce(m.subscription_status, 'none')       as subscription_status,
    coalesce(u.active_users_30d, 0)               as active_users_30d,
    strftime(u.last_event_at, '%Y-%m-%dT%H:%M:%SZ') as last_event_at
from customers c
left join mrr m using (stripe_customer_id)
left join usage u on u.email_domain = c.email_domain;
