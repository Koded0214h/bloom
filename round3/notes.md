i checked the test that failed, it linked to make() as a funciton in the file, and started analyzing the func. 
the test for test_cancelled_subscription_is_not_billed(): is failig cause "find_billable() == []" meaning sth could be billable there..
the start_day has an issue there.. we'd need to have a check before the arithemtic to cacl remianing days. for "test_full_month_when_started_on_the_first"


1st, prolly a date issue calc
a


ttl, time, bug
cache is throwing away necessary stuff, and keeping unnecessary things