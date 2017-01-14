# harpy
Dockerized Pythonic Chrome HAR capturer!

Harpy captures Chrome HTTP Archive (HAR) from a headless Chrome, using webdriver.
Based a lot on the [speedprofile](https://github.com/parasdahal/speedprofile) project, which has built the foundations to the container and webdriver communication.
The container is running [Supervisord](http://supervisord.org/) for process managing.

### Configuration

Using the `conf.yml` one can set the next:
* `url`: The url to sample
* `cycle_time`: Time of seconds between next sample
* `error_theshold`: Number of errors from which to send an email notification
* `email`: Boolean (true/false) determines whether email notification is activated

### Setup

1. `docker build -t harpy`
2. `docker run harpy`

That's it. The app is running.



