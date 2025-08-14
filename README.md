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
    <a href="https://github.com/tauassar/mockintosh/stargazers">
        <img alt="GitHub Stars" src="https://img.shields.io/github/stars/tauassar/mockintosh?logo=GitHub&style=flat-square">
    </a>
    <a href="https://github.com/tauassar/mockintosh/network">
        <img alt="GitHub Forks" src="https://img.shields.io/github/forks/tauassar/mockintosh?logo=GitHub&style=flat-square">
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

### Install with Docker

Pull and run the latest Mockintosh image from GitHub Container Registry:

```shell
# Pull the latest image
$ docker pull ghcr.io/tauassar/mockintosh:latest

# Run with a sample configuration
$ docker run -p 8000:8000 -p 8001:8001 ghcr.io/tauassar/mockintosh:latest --sample-config example.yaml

# Run with your own configuration
$ docker run -p 8000:8000 -p 8001:8001 -v $(pwd):/app/configs ghcr.io/tauassar/mockintosh:latest /app/configs/config.yaml
```

**Available Docker tags:**
- `ghcr.io/tauassar/mockintosh:latest` - Latest stable release
- `ghcr.io/tauassar/mockintosh:main` - Latest from main branch
- `ghcr.io/tauassar/mockintosh:v1.2.3` - Specific version
- `ghcr.io/tauassar/mockintosh:local` - Development version

**Ports:**
- `8000` - Mock service port
- `8001` - Management UI port

**Volumes:**
- Mount your configuration files to `/app/configs`
- Mount data directory to `/app/data` for persistent data
- Mount logs directory to `/app/logs` for log files

### Use Demo Sample Config

Run following command to generate `example.yaml` file in the current directory:

```shell
$ mockintosh --sample-config example.yaml
```

then, run that config with Mockintosh:

```shell
$ mockintosh example.yaml
```

And open http://localhost:9999 in your web browser.

You can also issue some CURL requests against it:

```shell
curl -v http://localhost:8888/

curl -v http://localhost:8888/api/myURLParamValue123/action

curl -v "http://localhost:8888/someMoreFields?qName1=qValue&qName2=12345" -X POST -H"X-Required-Header: someval" --data "payload"
```

## Command-line Arguments

The list of command-line arguments can be seen by running `mockintosh --help`.

If you don't want to listen all of the services in a configuration file then you can specify a list of service
names (`name` is a string attribute you can set per service):

```shell
$ mockintosh example.yaml 'Mock for Service1' 'Mock for Service2'
```

Using `--quiet` and `--verbose` options the logging level can be changed.

Using `--bind` option the bind address for the mock server can be specified, e.g. `mockintosh --bind 0.0.0.0`

Using `--enable-tags` option the tags in the configuration file can be enabled in startup time,
e.g. `mockintosh --enable-tags first,second`

## OpenAPI Specification to Mockintosh Config Conversion (_experimental_)

_Note: This feature is experimental. One-to-one transpilation of OAS documents is not guaranteed._

It could be a good kickstart if you have already an OpenAPI Specification for your API. Mockintosh is able to transpile
an OpenAPI Specification to its own config format in two different ways:

### CLI Option `--convert`

Using the `--convert` one can convert an OpenAPI Specification to Mockintosh config.

JSON output example:
```shell
$ wget https://petstore.swagger.io/v2/swagger.json
$ mockintosh swagger.json -c new_config.json json
```

YAML example:
```shell
$ mockintosh swagger.json -c new_config.yaml yaml
```

### Automatic Conversion

If you start Mockintosh with a valid OpenAPI Specification file then it automatically detects that the input is an
OpenAPI Specification file:

```shell
$ mockintosh swagger.json
```

and automatically starts itself from that file. Without producing any new files. So you can start to edit this file
through the management UI without even restarting Mockintosh.

## Development Setup

### Requirements Structure

Mockintosh uses a modular requirements structure following the cookiecutter-django pattern:

```
requirements/
├── base.txt            # Core dependencies for all environments
├── local.txt           # Local development dependencies
├── production.txt      # Production dependencies
├── test.txt            # Testing dependencies
└── ci.txt              # Continuous integration dependencies
```

**Installation by environment:**
```shell
# Development
pip install -r requirements/local.txt

# Production
pip install -r requirements/production.txt

# Testing
pip install -r requirements/test.txt

# CI
pip install -r requirements/ci.txt
```

### Docker Development

For local development with Docker:

```shell
# Build local development image
docker build -f docker/local/Dockerfile -t mockintosh:local .

# Run with hot reload
docker run -p 8000:8000 -p 8001:8001 \
  -v $(pwd):/app \
  -v $(pwd)/configs:/app/configs:ro \
  -v $(pwd)/data:/app/data \
  mockintosh:local
```

**Available Docker environments:**
- `docker/local/` - Local development with hot reload
- `docker/production/` - Production-optimized builds
- `docker-compose.yml` - Main compose file with profiles

**Quick start with Make:**
```shell
make dev          # Build and run local development
make prod         # Build and run production
make up-full      # Start all services (Kafka, Redis, etc.)
```

## Continuous Integration & Deployment

### GitHub Actions

Mockintosh uses GitHub Actions for automated CI/CD with the following workflow:

**`docker-image.yml`** - Automated Docker image builds:
- **Triggers**: Push to main, tags (v*), pull requests
- **Platforms**: Linux AMD64 and ARM64
- **Registry**: GitHub Container Registry (ghcr.io)
- **Security**: Trivy vulnerability scanning
- **Testing**: Basic container functionality tests

**Workflow Features:**
- Multi-platform Docker builds (AMD64/ARM64)
- Automatic tagging based on git events
- GitHub Actions cache for faster builds
- Security scanning with SARIF output
- Pull request validation (builds without pushing)

**Available Images:**
- `ghcr.io/tauassar/mockintosh:latest` - Latest stable release
- `ghcr.io/tauassar/mockintosh:main` - Latest from main branch
- `ghcr.io/tauassar/mockintosh:v1.2.3` - Specific version tags
- `ghcr.io/tauassar/mockintosh:main-abc123` - Commit-specific tags

**View Workflow:**
- [Docker Image CI](https://github.com/tauassar/mockintosh/actions/workflows/docker-image.yml)
- [Container Registry](https://github.com/tauassar/mockintosh/pkgs/container/mockintosh)

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
