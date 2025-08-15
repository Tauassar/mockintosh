# Mockintosh

<p align="center">
    <a href="https://github.com/tauassar/mockintosh/releases/latest">
        <img alt="GitHub Latest Release" src="https://img.shields.io/github/v/release/tauassar/mockintosh?logo=GitHub&style=flat-square">
    </a>
    <a href="https://github.com/tauassar/mockintosh/blob/master/LICENSE">
        <img alt="GitHub License" src="https://img.shields.io/github/license/tauassar/mockintosh?logo=GitHub&style=flat-square">
    </a>
    <a href="https://github.com/tauassar/mockintosh/actions/workflows/docker-image.yml">
        <img alt="Docker Build Status" src="https://img.shields.io/github/actions/workflow/status/tauassar/mockintosh/docker-image.yml?logo=GitHub&style=flat-square">
    </a>
    <a href="https://github.com/tauassar/mockintosh/actions/workflows/docker-image.yml">
        <img alt="Docker Image" src="https://img.shields.io/github/actions/workflow/status/tauassar/mockintosh/docker-image.yml?label=Docker%20Image&logo=docker&style=flat-square">
    </a>
    <a href="https://github.com/tauassar/mockintosh/pkgs/container/mockintosh">
        <img alt="GitHub Container Registry" src="https://img.shields.io/badge/GHCR-mockintosh-blue?logo=github&style=flat-square">
    </a>
    <a href="https://codecov.io/gh/tauassar/mockintosh">
        <img alt="Code Coverage (Codecov)" src="https://img.shields.io/codecov/c/github/tauassar/mockintosh?logo=Codecov&style=flat-square">
    </a>
</p>

## Quick Links

[**Documentation Website**](https://mockintosh.io/)

[**YouTube Video Series**](https://www.youtube.com/watch?v=Q8RPT6TPOIg&list=PLJE3O0IuP-IZMWEOI8dU0U3rO_CPPhLv9)

[**Bug Tracker**](https://github.com/tauassar/mockintosh/issues)

[**Slack**](https://up9.slack.com/)

[**Stack Overflow**](https://stackoverflow.com/questions/tagged/mockintosh)

[**Faker API Reference**](https://faker.readthedocs.io/en/master/providers.html)

## About

You've just found a new way of mocking microservices!

![Control Plane](https://i.ibb.co/3kG9xMr/Screenshot-from-2021-07-07-12-53-40.png)

An example config that demonstrates the common features of Mockintosh:

```yaml
services:
  - name: Mock for Service1
    hostname: localhost
    port: 8000
    managementRoot: __admin  # open http://localhost:8001/__admin it in browser to see the UI  
    endpoints:

      - path: "/"  # simplest mock

      - path: "/api/users/{{param}}"  # parameterized URLs
        response: "simple string response with {{param}} included"

      - path: /comprehensive-matching-and-response
        method: POST
        queryString:
          qName1: qValue  # will only match if query string parameter exists
          qName2: "{{regEx '\\d+'}}"  # will require numeric value
        headers:
          x-required-header: someval  # will cause only requests with specific header to work
        body:
          text: "{{regEx '.+'}}"  # will require non-empty POST body
        response: # the mocked response specification goes below
          status: 202
          body: "It worked"
          headers:
            x-response-header: "{{random.uuid4}}"  # a selection of random/dynamic functions is available
            x-query-string-value: "{{request.queryString.qName2}}"  # request parts can be referenced in response

```

Mockintosh is a service virtualization tool that's capable to generate mocks for **RESTful APIs** and communicate
with **message queues**
to either mimic **asynchronous** tasks or to simulate **microservice architectures** in a blink of an eye.

The state-of-the-art mocking capabilities of Mockintosh enables software development teams to work
**independently** while building and maintaining a **complicated** microservice architecture.

Key features:

- Multiple services mocked by a single instance of Mockintosh
- Lenient [configuration syntax](https://mockintosh.io/Configuring.html)
- Remote [management UI+API](https://mockintosh.io/Management.html)
- Request scenarios support with [multi-response endpoints](https://mockintosh.io/Configuring.html#multiple-responses)
  and [tags](https://mockintosh.io/Configuring.html#tagged-responses)
- [Mock Actor](https://mockintosh.io/Async.html) pattern for Kafka, RabbitMQ, Redis and some other message bus protocols
- GraphQL queries recognizing

_[In this article](https://up9.com/open-source-microservice-mocking-introducing-mockintosh) we explain how and why
Mockintosh was born as a new way of mocking microservices._

## Quick Start

### Install on MacOS

Install Mockintosh app on Mac using [Homebrew](https://brew.sh/) package manager:

```shell
$ brew install tauassar/repo/mockintosh
```
### Install on Windows

Download an installer from [releases](https://github.com/tauassar/mockintosh/releases) section and launch it. Follow the steps in wizard to install Mockintosh.

### Install on Linux

Install Mockintosh Python package using [`pip`](https://pypi.org/project/pip/) (or `pip3` on some machines):

```shell
$ pip install -U mockintosh
```

### Use Demo Sample Config

Run following command to generate `example.yaml` file in the current directory:

```shell
$ mockintosh sample-config example.yaml
```

then, run that config with Mockintosh:

```shell
$ mockintosh serve example.yaml
```

And open http://localhost:9999 in your web browser.

You can also issue some CURL requests against it:

```shell
curl -v http://localhost:8888/

curl -v http://localhost:8888/api/myURLParamValue123/action

curl -v "http://localhost:8888/someMoreFields?qName1=qValue&qName2=12345" -X POST -H"X-Required-Header: someval" --data "payload"
```

## Command-line Interface

Mockintosh provides a modern, organized command-line interface with clear subcommands:

### Generate Sample Configuration

```shell
# Generate sample config with default name
$ mockintosh sample-config

# Generate sample config with custom name
$ mockintosh sample-config my-config.yaml
```

### Convert OpenAPI Specifications

```shell
# Convert OpenAPI spec to Mockintosh config
$ mockintosh convert swagger.json config.yaml

# Specify output format (json or yaml)
$ mockintosh convert swagger.json config.json json
```

### Start the Server

```shell
# Start server with configuration file
$ mockintosh serve config.yaml

# Start specific services only
$ mockintosh serve config.yaml --services "Service1" "Service2"

# Enable specific tags
$ mockintosh serve config.yaml --tags "dev,test"

# Load custom interceptors
$ mockintosh serve config.yaml --interceptors "myapp.interceptors.auth" "myapp.interceptors.logging"
```

### Global Options

All commands support these global options:

```shell
$ mockintosh --quiet --bind 0.0.0.0 serve config.yaml
$ mockintosh --verbose --debug --logfile app.log serve config.yaml
```

**Available Options:**
- `-q, --quiet`: Less logging messages, only warnings and errors
- `-v, --verbose`: More logging messages, including debug
- `-l, --logfile`: Also write log into a file
- `-b, --bind`: Address to specify the network interface
- `--debug`: Enable debug mode
- `--help`: Show help message

### Examples

```shell
# Quick start with sample config
$ mockintosh sample-config
$ mockintosh serve sample-config.yaml

# Development with verbose logging
$ mockintosh --verbose --debug serve dev-config.yaml

# Production with specific bind address
$ mockintosh --quiet --bind 0.0.0.0 serve prod-config.yaml

# Convert existing OpenAPI spec
$ mockintosh convert api-spec.yaml mockintosh-config.yaml yaml
```

## Docker

```shell
# Pull the latest image
$ docker pull ghcr.io/tauassar/mockintosh:latest

# Run with a sample configuration
$ docker run -p 8000:8000 -p 8001:8001 ghcr.io/tauassar/mockintosh:latest sample-config
$ docker run -p 8000:8000 -p 8001:8001 ghcr.io/tauassar/mockintosh:latest serve sample-config.yaml

# Run with your own configuration
$ docker run -p 8000:8000 -p 8001:8001 -v $(pwd):/app/configs ghcr.io/tauassar/mockintosh:latest serve /app/configs/config.yaml
```

## Build the Docs

Single-command from `/docs` to review docs locally:
```shell
docker run -p 8080:4000 -v $(pwd):/site bretfisher/jekyll-serve
```

Or manual:

Install [Jekyll](https://jekyllrb.com/) and [Bundler](https://bundler.io/):

```shell
$ gem install jekyll bundler
```

Install the gems:

```shell
$ cd docs/
$ bundle config set --local path 'vendor/bundle'
$ bundle install
```

Run the server:

```shell
$ bundle exec jekyll serve
```

## OpenAPI Specification to Mockintosh Config Conversion

_Note: This feature is experimental. One-to-one transpilation of OAS documents is not guaranteed._

Mockintosh can convert OpenAPI Specifications to its own config format using the `convert` command:

```shell
# Convert to YAML (default)
$ mockintosh convert swagger.json config.yaml

# Convert to JSON
$ mockintosh convert swagger.json config.json json

# Example with real OpenAPI spec
$ wget https://petstore.swagger.io/v2/swagger.json
$ mockintosh convert swagger.json petstore-config.yaml
```

The conversion provides a good starting point if you already have an OpenAPI Specification for your API.
