# Ax_Metrics - "BI Glue" Business Intelligence middleware Python library





## Overview


Ax_Metrics is an Business Intelligence (BI) open source Python middleware library facilitating aggregation of metrics and KPIs from any source and custom reporting for humans or other APIs.



### Target Problem

  1. You have multiple systems of all scales generating metrics and logs.

  2. Your centralized or distributed Data Warehouse (DW) collects this data, indexes it by time, and makes it available.

  3. You want fast, friendly, pretty, clean access to KPIs that will help you grow your business.  

  4. Most solutions are incompatible, insecure, expensive, or far too complex.

  5. You have technical knowledge at least on the level of understanding HTML, XML, YAML, etc.



### The Solution: Ax_Metrics


Ax_Metrics is a library to empower BI initiatives.  The *components described below* work together to comprise a powerful hub for connecting data, processing it, and getting it where it needs to be.


#### MDefL
Ax_Metrics **Metrics Definition Language** - Model your metrics and KPIs (Key Performance Indicators) with just a few lines of this YAML-based definition language, defining where and how they're located, indexed, and typed.  *Some example metric sets ("MetSets") used by automated tests: [metset1.yml](./tests/assets/metset1.yml) and [metset-http.yml](./tests/assets/metset-http.yml).*

#### EMFetch 
Ax_Metrics **Extensible Metrics Fetch** - The EMFetch engine provides low level access to raw time-indexed metrics data for the rest of Ax_Metrics.  Metrics described by your MDefL reference the EMFetch plugin used to access them.  *Plugins like [emf_http](./py/axonchisel/metrics/io/emfetch/plugins/emf_http.py) are available for use, or extend them with your own Python code to easily integrate with any custom data source.*

#### MQL
Ax_Metrics **Metrics Query Language** - Create MQL queries in this YAML-based query language to slice, dice, time shift, forecast, smooth, compare, and format your data into reports for humans or other APIs.  *An example query used by automated tests can be seen in [mqe-query2.yml](./tests/assets/mqe-query2.yml), while an even more complex query set containing multiple pre-defined queries can be seen in [queryset2.yml](./tests/assets/queryset2.yml).*

#### MQEngine
Ax_Metrics **Metrics Query Engine** - Embed MQEngine in your BI flow or place it behind a web server to process MQL queries on demand, within any security/authorization layer and web app you already use.  MQEngine is the Ax_Metrics core that processes any query you throw at it and yields data sets.

#### EROut
Ax_Metrics **Extensible Report Outputter** - ERout outputters present data reports from MQEngine in many formats, for humans or further API consumption.  *Plugins like [csv](./py/axonchisel/metrics/io/erout/plugins/ero_csv.py) and [geckoboard_numsec](./py/axonchisel/metrics/io/erout/plugins/ero_geckoboard/numsec.py) (for your 60" LCD dashboard powered by [Geckoboard](http://www.geckoboard.com/)) are available for use, or extend them with your own Python code to easily integrate with other any data consumer, human or machine.*

#### Servant
Ax_Metrics **Servant** - The high layer Servant is available to wrap everything up in a convenient package.  This is the recommended integration point for most Ax_Metrics use: *build a [Servant](./py/axonchisel/metrics/run/servant/servant.py) around a [ServantConfig](./py/axonchisel/metrics/run/servant/config.py) object, then construct [ServantRequest](./py/axonchisel/metrics/run/servant/request.py) objects and feed them to the Servant.  This is also the best place to start if you want to dig into the Ax_Metrics code itself, as it leads to all other pieces. See [test_servant.py](./tests/test_servant.py) for test code that invokes Servant.*




### Ax_Metrics is *NOT...*


#### NOT a web service
Ax_Metrics does NOT include any web services or APIs that run in the background or require hosting or IT/DevOps support.  It is a software library to utilize and integrate as you see fit.  (Though it does include some helper routines to make integrating with your own web environment easier.)

#### NO persistence DW capabilities
Ax_Metrics fetches data dynamically and generates reports on demand.  Some data may be cached for performance purposes, but this cache should be considered a volatile implementation detail only.  Your data is assumed to already persist in a queryable form.

#### NOT a turnkey solution
Ax_Metrics requires custom integration into DW sources, custom definition of metrics and reports, and often customization of output formats.  It is a powerful and time-saving support library for use in BI data visualization projects, but it is not a magic bullet.

#### NOT a visualizer or chart generator
Ax_Metrics is designed to be used *with* visualization and charting (or other) output systems.  It is a middleware library that helps fetch, analyze, and wrangle your data into a format ready to be visualized.


### "Can't I can just use SQL instead?"


If your data already exists in a relational database, then you already have direct access to it.  You can write SQL queries to generate various reports, but as you analyze more deeply, your queries will become complex, slow, and eventually impossible, requiring additional processing outside of your DB.

Review various 3rd party charting packages and you'll see mostly simplistic examples like "sales per month by region" which are easily queryable from raw data.  That's a great start, but it will only get your BI efforts so far.

Ax_Metrics treats raw time series data (such as might be stored and queryable in a relational DB) as the *input* to deeper BI analysis.  Read on to see some examples of the types of reports it can produce. And in addition to higher level analysis, Ax_Metrics can also provide ties in to multiple DW sources as well as the foundation for your metrics definitions and queries, all written in the high-level user-friendly languages MDefL and MQL, allowing you to focus on your own personal business metrics instead of reinventing the wheel.

In summary, you can use SQL (or anything else) to query raw time series data, but when you layer Ax_Metrics on top of that, you add intelligence and move your data closer to more powerful and useful visualization and analysis.




## Examples of Use



### Example Metrics


Anything that can be measured numerically over some period of time is a valid metric.  

Examples:

  - new trials
  - new sales
  - new revenue
  - invites sent
  - invites read
  - invites accepted
  - web visitors
  - web requests
  - expenses
  - app server errors


### Example Reports


Once your metrics are defined and the EMFetch plugins integrated with your data sources, a wide variety of reports can be easily built to view that data.  Much of the power of Ax_Metrics arises out of the rich time frame model and query language.

Examples:

  - amount per 5 minutes for the last 6 hours
  - daily amount over past 30 days, compared to same 30 day period 1 year ago *(e.g. visualized as multi-series (2) line chart)*
  - amount in current calendar week to date, compared to previous week and same week 1 year ago *(e.g. as multi-series (3) line chart)*
  - amount in calendar month to date, compared to forecast amount *(e.g. visualized as bullet chart)*
  - amount in last completed calendar quarter, measured weekly with 30 day smoothing, compared to forecast amount, previous quarter, and same quarter last 2 years *(e.g. visualized as multi-series (5) line chart)*






## Installation


### Install with pip

    $ pip install ax_metrics






## Meta



### Status

Created 2014-11.  Initial implementation released.


### Requirements

  - Python 2.6+  (Python 3 is not supported at this time)
  - A few small PyPi packages that should be installed automatically if you use pip.  (See [setup.py](./setup.py) for details)


### Official Links

Source repository & issue tracker:

  - https://github.com/axonchisel/ax_metrics


### License

This open source software is licensed under the permissive [MIT license](http://choosealicense.com/licenses/mit/).  The full license text can be found in [LICENSE.txt](./LICENSE.txt) within this repo.


### Developers

Interested in digging in to the Ax_Metrics code and possibly contributing?  Here are some essential links:

  - [Developers Overview Guide](./docs/developers.md) - contributing, project structure, etc.
  - https://github.com/axonchisel/ax_metrics - GitHub official page


### Genesis

This project was inspired in late 2014 by a need to effectively digest and visualize large amounts of business metrics -- to measure, guide, challenge, and inspire.  The source code is cleaned and released under a liberal license in the hopes that others will find it useful and build on it.



### History


#### Version 0.9.1 (2014-12-08)

- First public release.


#### Version 0.0.0 (2014-11-07)

- Project created.








------------------------------------------------------------------------------

Ax_Metrics - Copyright (c) 2014 Dan Kamins, AxonChisel.net

