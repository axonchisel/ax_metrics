
# Ax_Metrics Developers Overview

This document is not required reading for *using* Ax_Metrics.  For an introduction and general user information, please see the [README](../README.md).

Ax_Metrics is a library targeted largely at developers, designed to empower BI initiatives.  These users may gain helpful or interesting background information here.

But this document is aimed primarily at developers looking to work with and contribute to the actual Ax_Metrics project itself.



## Source Code & Contributing

Fork, submit pull requests, report issues, and discuss at:

  - https://github.com/axonchisel/ax_metrics - GitHub official page


## Technical Overview


### Project Structure

```
/                                                             axonchisel
|
|
+-- py/                                                 Python code root
|   |
|   +-- axonchisel/                                           axonchisel
|       |                           (top level shared package namespace)
|       ...                       (see "Python Package Hierarchy" below)
|
+-- tests/                          (full package py.test test coverage)
|   |
|   +-- assets/                   (assets for testing: MQL, MDefL, etc.)
|
+-- docs/                                                (documentation)

```


### Python Package Hierarchy

```
/py/axonchisel/                                               axonchisel
|                                   (top level shared package namespace)
|
|
+-- metrics/                                          axonchisel.metrics
    |                                               (Ax_Metrics project)
    |   
    |   
    +-- run/                                      axonchisel.metrics.run
    |   |                                (processing queries at runtime)
    |   | 
    |   +-- servant/                      axonchisel.metrics.run.servant
    |   |                   (wraps fetch, query, engine, report process)
    |   |                     
    |   +-- mqengine/                    axonchisel.metrics.run.mqengine
    |                                   (process queries to obtain data)
    |                                  (MQEngine = Metrics Query Engine)
    |                                    
    |                                    
    +-- io/                                        axonchisel.metrics.io
    |   |                      (connections to the world: stats, output)
    |   | 
    |   +-- emfetch/                       axonchisel.metrics.io.emfetch
    |   |                           (plugins to access raw metrics data)
    |   |                         (EMFetch = Extensible Metrics Fetcher)
    |   |        
    |   +-- erout/                           axonchisel.metrics.io.erout
    |                         (plugins to output various report formats)
    |                              (ERout = Extensible Report Outputter)
    |                                
    |                                
    +-- foundation/                        axonchisel.metrics.foundation
        |                             (core data models, logic, parsers)
        | 
        +-- ax/                         axonchisel.metrics.foundation.ax
        |                            (common base classes and utilities)
        |
        |
        +-- query/                   axonchisel.metrics.foundation.query
        |                                     (query models, MQL parser)
        |                                 (MQL = Metrics Query Language)
        |                                   
        +-- data/                     axonchisel.metrics.foundation.data
        |                            (time range x value points, series)
        |                              
        +-- metricdef/           axonchisel.metrics.foundation.metricdef
        |                            (core metrics models, MDefL parser)
        |                          (MDefL = Metrics Definition Language)
        |                            
        +-- chrono/                 axonchisel.metrics.foundation.chrono
                                      (Time-related models, math, logic)

```


### Architecture / Dependency Graph

```

                                          RUN HERE
                                        _____v______                 
    /                                  |            |                
   |                                   |  servant   |                
   |R                                  |____________|                
   |U                                   |         |           
   |N                         __________|_        |           
   |                         |            |       |           
   |                         |  mqengine  |       |           
    \                        |____________|       |           
                              |         |         |        
    /                _________|__       |        _|__________
   |I               |            |      |       |            |
   |O     METRICS <-|   emfetch  |      |       |    erout   |-> REPORTS
    \               |____________|      |       |____________|
                        |  |  |         |        |         |
    /                   |  |  |         |        |         |
   |F            _______|  |  |_____    |        |         |
   |O            |   ______|_____  |   _|________|_   .....|......   
   |U            |  |            | |  |            | :            :
   |N            |  |    data    | |  |   query    | :    data    :
   |D            |  |____________| |  |____________| :............:
   |A            |    |        |   |    |
   |T       _____|____|_      _|___|____|_
   |I      |            |    |            |
   |O      | metricdef  |    |   chrono   |
   |N      |____________|    |____________|
    \

```





------------------------------------------------------------------------------

*Return to the [README](../README.md)*

------------------------------------------------------------------------------

Ax_Metrics - Copyright (c) 2014 Dan Kamins, AxonChisel.net
