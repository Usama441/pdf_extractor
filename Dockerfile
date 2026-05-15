# syntax=docker/dockerfile:1

ARG RUBY_VERSION=3.3.3
FROM ruby:${RUBY_VERSION}-slim

WORKDIR /rails

ENV BUNDLE_PATH="/usr/local/bundle" \
    BUNDLE_JOBS="4" \
    BUNDLE_RETRY="3" \
    PIP_NO_CACHE_DIR="1" \
    PYTHON_EXTRACTOR_BIN="/opt/pdf-extractor-venv/bin/python" \
    PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1"

RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
      build-essential \
      git \
      libpq-dev \
      libvips \
      pkg-config \
      postgresql-client \
      python3 \
      python3-dev \
      python3-pip \
      python3-venv && \
    rm -rf /var/lib/apt/lists /var/cache/apt/archives

COPY Gemfile Gemfile.lock requirements.txt ./

RUN bundle install
RUN python3 -m venv /opt/pdf-extractor-venv && \
    /opt/pdf-extractor-venv/bin/python -m pip install --upgrade pip && \
    /opt/pdf-extractor-venv/bin/python -m pip install -r requirements.txt

COPY . .

RUN chmod +x /rails/bin/docker-entrypoint /rails/bin/jobs

ENTRYPOINT ["/rails/bin/docker-entrypoint"]
EXPOSE 3000
CMD ["bundle", "exec", "rails", "server", "-b", "0.0.0.0", "-p", "3000"]
