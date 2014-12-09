"""
Ax_Metrics - datetime math utilities

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from datetime import datetime, timedelta


# ----------------------------------------------------------------------------


def add(dt,
        years=0, quarters=0, months=0, weeks=0, days=0,
        hours=0,
        minutes5=0, minutes10=0, minutes15=0, minutes30=0,
        minutes=0,
        seconds=0, milliseconds=0, microseconds=0
    ):
    """
    Given a datetime.datetime obj, add or subtract specified amounts of time,
    returning new datetime obj.
    """
    if microseconds:
        dt = add_microseconds(dt, microseconds)
    if milliseconds:
        dt = add_microseconds(dt, 1000*milliseconds)
    if seconds:
        dt = add_seconds(dt, seconds)
    if minutes:
        dt = add_minutes(dt, minutes)
    if minutes5:
        dt = add_minutes(dt, 5 * minutes5)
    if minutes10:
        dt = add_minutes(dt, 10 * minutes10)
    if minutes15:
        dt = add_minutes(dt, 15 * minutes15)
    if minutes30:
        dt = add_minutes(dt, 30 * minutes30)
    if hours:
        dt = add_hours(dt, hours)
    if days:
        dt = add_days(dt, days)
    if weeks:
        dt = add_weeks(dt, weeks)
    if months:
        dt = add_months(dt, months)
    if quarters:
        dt = add_quarters(dt, quarters)
    if years:
        dt = add_years(dt, years)
    return dt


# ----------------------------------------------------------------------------


def begin_year(dt):
    """Return datetime marking beginning of year containing dt."""
    return dt.replace(  microsecond=0, second=0, minute=0, hour=0, 
                        day=1, month=1)

def begin_quarter(dt):
    """Return datetime marking beginning of quarter containing dt."""
    quarter0 = ((dt.month - 1) / 3)
    month = quarter0 * 3 + 1
    return dt.replace(  microsecond=0, second=0, minute=0, hour=0, 
                        day=1, month=month)

def begin_month(dt):
    """Return datetime marking beginning of month containing dt."""
    return dt.replace(  microsecond=0, second=0, minute=0, hour=0, 
                        day=1)

def begin_week(dt, day0_sunday_ofs=0):
    """
    Return datetime marking beginning of week containing dt.
    If day0_sunday_ofs specified, it is treated as day offset from Sunday
    indicating what first day of week is, e.g. 1=Monday, -1=Saturday.
    """
    dt = begin_day(dt)
    weekday = dt.weekday() # (Mon=0, Sun=6)
    weekday = (weekday + 1) % 7  # (Sun=0, Sat=6)
    day0 = day0_sunday_ofs % 7
    days_off = (weekday - day0) % 7
    td = timedelta(days=-days_off)
    return dt + td

def begin_day(dt):
    """Return datetime marking beginning of day containing dt."""
    return dt.replace(microsecond=0, second=0, minute=0, hour=0)

def begin_hour(dt):
    """Return datetime marking beginning of hour containing dt."""
    return dt.replace(microsecond=0, second=0, minute=0)

def begin_minute30(dt):
    """Return datetime marking beginning of 30-min period containing dt."""
    minutes = dt.minute / 30 * 30
    return dt.replace(microsecond=0, second=0, minute=minutes)

def begin_minute15(dt):
    """Return datetime marking beginning of 15-min period containing dt."""
    minutes = dt.minute / 15 * 15
    return dt.replace(microsecond=0, second=0, minute=minutes)

def begin_minute10(dt):
    """Return datetime marking beginning of 10-min containing dt."""
    minutes = dt.minute / 10 * 10
    return dt.replace(microsecond=0, second=0, minute=minutes)

def begin_minute5(dt):
    """Return datetime marking beginning of 5-min containing dt."""
    minutes = dt.minute / 5 * 5
    return dt.replace(microsecond=0, second=0, minute=minutes)

def begin_minute(dt):
    """Return datetime marking beginning of minute containing dt."""
    return dt.replace(microsecond=0, second=0)

def begin_second(dt):
    """Return datetime marking beginning of second containing dt."""
    return dt.replace(microsecond=0)


# ----------------------------------------------------------------------------


def add_years(dt, delta):
    """Return datetime offset by +/- delta years."""
    val = dt.year + delta
    return dt.replace(year=val)

def add_quarters(dt, delta):
    """Return datetime offset by +/- delta quarters."""
    return add_months(dt, delta * 3)

def add_months(dt, delta):
    """Return datetime offset by +/- delta months."""
    val = dt.month + delta
    if val > 12:
        carry = (val - 1) / 12
        val -= (carry * 12)
        dt = add_years(dt, carry)
    if val <= 0:
        borrow = -((val - 1) / 12)
        val += (borrow * 12)
        dt = add_years(dt, -borrow)
    return dt.replace(month=val)

def add_weeks(dt, delta):
    """Return datetime offset by +/- delta weeks."""
    return dt + timedelta(days=7*delta)

def add_days(dt, delta):
    """Return datetime offset by +/- delta days."""
    return dt + timedelta(days=delta)

def add_hours(dt, delta):
    """Return datetime offset by +/- delta hours."""
    return dt + timedelta(seconds=60*60*delta)

def add_minutes(dt, delta):
    """Return datetime offset by +/- delta minutes."""
    return dt + timedelta(seconds=60*delta)

def add_minute5s(dt, delta):
    """Return datetime offset by +/- delta 5-minute increments."""
    return dt + timedelta(seconds=5*60*delta)

def add_minute10s(dt, delta):
    """Return datetime offset by +/- delta 10-minute increments."""
    return dt + timedelta(seconds=10*60*delta)

def add_minute15s(dt, delta):
    """Return datetime offset by +/- delta 15-minute increments."""
    return dt + timedelta(seconds=15*60*delta)

def add_minute30s(dt, delta):
    """Return datetime offset by +/- delta 30-minute increments."""
    return dt + timedelta(seconds=30*60*delta)

def add_seconds(dt, delta):
    """Return datetime offset by +/- delta seconds."""
    return dt + timedelta(seconds=delta)

def add_microseconds(dt, delta):
    """Return datetime offset by +/- delta microseconds."""
    return dt + timedelta(microseconds=delta)


# ----------------------------------------------------------------------------


# (See test suite in axonchisel.metrics.tests.test_dtmath)

