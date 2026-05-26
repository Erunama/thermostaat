# Thermostaat
![GitHub Release](https://img.shields.io/github/v/release/Erunama/thermostaat?include_prereleases&display_name=tag&style=flat-square)

BE WARNED: VERY WIP

A wrapper for the Tado X valve controlers to integrate to home assistant via matter but keep similar useability.

The goal is to thus mimic and expand what I see as key features:
 - Scheduling per day, with a copy logic [WIP]
 - Manual override mode: when the valve is changed it temporarily suspends the schedule temp.
 - Away mode: when away it should go it to a set base temp
 - Window mode: when the/a/all window(s) in a room are opened turn off the radiator

Currently it supports a very basic scheduling. Will be part of settings, probably not enabled standard but this hasn't been finished.
Example schedule:

```json
[
  {
    "time": "08:00",
    "temperature": 21
  },
  {
    "time": "22:00",
    "temperature": 18
  }
]
```


## AI Usage
I have used chatgpt as a development tool. 
