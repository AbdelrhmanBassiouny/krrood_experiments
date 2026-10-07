# Experiments of the KRROOD paper: GraphDB 11.2 (official image, Ubuntu 24.04, Java 21) with Python 3.12,
# the earlier version of KRROOD that the experiments use, and the current version that the listings use.
FROM ontotext/graphdb:11.2.0

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

# Python 3.12, and what pygraphviz needs to build; git only answers "not a repository" in the environment record.
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3.12 python3.12-venv python3.12-dev build-essential \
       graphviz libgraphviz-dev pkg-config git \
    && rm -rf /var/lib/apt/lists/*

# Nemo 0.10.1 (in-memory Datalog engine; the nemo_owlrl baseline), the release binary checked against the sha256 that
# the release publishes (nemo_v0.10.1_x86_64-unknown-linux-gnu.tar.gz.sha256sum). It needs only glibc.
ARG NEMO_VERSION=0.10.1
ARG NEMO_SHA256=2f659c3803fa7b9a4ce1c9449803038e04562d74d83e5cd325cca43b4fcdd6f9
RUN curl -fsSL -o /tmp/nemo.tar.gz \
       "https://github.com/knowsys/nemo/releases/download/v${NEMO_VERSION}/nemo_v${NEMO_VERSION}_x86_64-unknown-linux-gnu.tar.gz" \
    && echo "${NEMO_SHA256}  /tmp/nemo.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/nemo \
    && tar xzf /tmp/nemo.tar.gz -C /opt/nemo --strip-components=1 \
    && rm /tmp/nemo.tar.gz \
    && ln -s /opt/nemo/nmo /usr/local/bin/nmo \
    && nmo --version
ENV NEMO_BINARY=/opt/nemo/nmo

# Third-party packages at the versions of the environment in which the results were verified.
COPY environment/ /opt/aamas27/environment/
RUN python3.12 -m venv /opt/venvs/earlier \
    && /opt/venvs/earlier/bin/pip install -q --upgrade pip \
    && /opt/venvs/earlier/bin/pip install -q --no-deps -r /opt/aamas27/environment/earlier-lock.txt \
    && python3.12 -m venv /opt/venvs/current \
    && /opt/venvs/current/bin/pip install -q --upgrade pip \
    && /opt/venvs/current/bin/pip install -q --no-deps -r /opt/aamas27/environment/current-lock.txt

COPY code/ /opt/aamas27/code/
RUN /opt/venvs/earlier/bin/pip install -q --no-deps -e /opt/aamas27/code/earlier/krrood \
       -e /opt/aamas27/code/earlier/ripple_down_rules -e /opt/aamas27/code/earlier/experiments \
    && /opt/venvs/current/bin/pip install -q --no-deps -e /opt/aamas27/code/current/krrood \
    && /opt/venvs/earlier/bin/python -c "import krrood, ripple_down_rules, krrood_experiments" \
    && /opt/venvs/current/bin/python -c "import krrood.entity_query_language.factories" \
    && ln -s /state/results /opt/aamas27/code/earlier/experiments/results \
    && ln -s /state/owl2bench_statements_reasoned.rdf \
       /opt/aamas27/code/earlier/experiments/resources/owl2bench_statements_reasoned.rdf

COPY listings/ /opt/aamas27/listings/
COPY tools/ /opt/aamas27/tools/
COPY reproduce.sh /opt/aamas27/reproduce.sh

WORKDIR /opt/aamas27/code/earlier/experiments
ENTRYPOINT ["bash", "/opt/aamas27/reproduce.sh"]
CMD ["quick"]
