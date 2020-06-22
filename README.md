# tap-nikabot

This is a [Singer](https://singer.io) tap that produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md) to retrieve [Nikabot](https://www.nikabot.com/) timesheeting data from the [Nikabot API](https://api.nikabot.com/swagger-ui.html#/).

## Quickstart

Install the package

```
$ pip install .
```

Discover the streams

```
$ tap-nikabot -c config.json --discover > catalog.json
```

Run the tap (you will need to edit the catalog to add `"selected": true` to a stream's metadata)

```
$ tap-nikabot -c config.json --catalog catalog.json
```

See the [Singer documentation](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md) for full usage.

## Streams

tap-nikabot supports the following streams:

- users
- roles
- groups
- teams
- projects
- records

Where records are the timesheet entries for a user.

## Config

A sample config is provided in `config_sample.json`.

| Property     | Default | Description                                                  |
| ------------ | ------- | ------------------------------------------------------------ |
| access_token | None    | **Required.** Nikabot API access token                       |
| page_size    | 1000    | Allows configuring the number of records returned in each server request. |
| start_date   | None    | The timesheet date to start pulling records from. If not provided will sync from the beginning of time. |
| end_date     | None    | The timesheet date to start pulling records up to. If not provided will sync up to todays date, but see note about cutoff days. |
| cutoff_days  | 10      | When using incremental replication, will only sync records up to this many days before todays date. |

### A note on bookmarks

Start date and end date take preferrence over bookmarks. If you have a bookmark that is earlier than the configured start date, syncing will start from start date. If you have a bookmark that is greater than end date, no records will be returned.

### Cutoff days

The Nikabot API only allows for filtering timesheet records by timesheet day, and only returns the created date not a modified date, his makes incremental replication a challenge. To support incremental replication, we've introduced a concept of cutoff days.

When `replication-method: "INCREMENTAL"` is specified in the catalog for the records stream, the timesheet date is used as a bookmark / replication key and the tap will only sync records up to "cutoff_days" (defaults to 10 days) before today. Users have the cutoff days period to enter their timesheet information after which their entries will not be synced. 

Note that because the timesheet date is a date only (not time), you will only be update to sync at most once per day.

Cutoff days cannot be combined with an end date in config. If an end date is provided, cutoff days will be ignored and records will be synced right up to end date.

#### Example

![Cutoff Days Example Diagram](docs/cutoff_days_example.png)

## Reformatted dates

The Nikabot API returns dates in ISO 8601format without any timezone information. This is not compatible with [JSON Schema which requires RFC 3339 formatted dates](https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.3), which are a subset of the ISO specification but mandates timezones. To allow the Nikabot data to be successfully vaidated against the schema, we post-process the data to add timezone information by assuming all dates are in UTC.

So `2019-09-02T05:13:43.151` becomes `2019-09-02T05:13:43.151000+00:00`.

This process uses the schema to determine which dates to reformat, if there is no schema information for the datetime field (e.g. blank schema `{}` ), then the dates will not be adjusted.

## Development

A Makefile is provided to manage a virtual environment.

```
$ make init
```

Will setup a [virtual environment](https://docs.python.org/3/tutorial/venv.html) in `.venv` and install the package and all (development and production) dependencies.

To run the linter / autoformatter (provided by [black](https://black.readthedocs.io/en/stable/)) 

```
$ make lint
```

To run the test suite (which also runs the linter)

```
$ make test
```

To run the tap in discovery mode (loads config from `config.json`)

```
$ make discover
```

Or to run it in sync mode (loads catalog from `catalog.json` and config from `config.json`)

```
$ make sync
```

### Proxying requests

You can proxy all requests through a proxy tool like OWASP ZAP, BurpSuite, Fiddler or Charles Proxy using environment variables to control the [python requests pacakge](https://requests.readthedocs.io/en/master/user/advanced/#proxies). And easy way to manage this is with a shell script that sets environment variables. Create the script `env.sh`:

```
#!/bin/sh
##
# Script to execute a command with specific environment variables set.
# Note that environment variables passed as arguments will need to be escaped to avoid shell expansion.
#
# USAGE:
#   ./env.sh my-command
#   ./env.sh 'echo $MY_VAR'
##

set -e

export HTTP_PROXY="http://localhost:8080"
export HTTPS_PROXY="http://localhost:8080"
export REQUESTS_CA_BUNDLE="C:\path\to\owasp_zap_root_ca.cer"

eval "$@"
```

Update REQUESTS_CA_BUNDLE to point to the CA certificate for the proxy tool. Now pass your command to the script to run it.

```
$ ./env.sh make discover > catalog.json
$ ./env.sh tap-nikabot -c config.json --catalog catalog.json
```
