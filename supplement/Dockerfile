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
COPY reproduce.sh /opt/aamas27/reproduce.sh

WORKDIR /opt/aamas27/code/earlier/experiments
ENTRYPOINT ["bash", "/opt/aamas27/reproduce.sh"]
CMD ["check"]
