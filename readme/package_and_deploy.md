


# Setup Editable Dev env
```shell
micromamba create   --name neat_build_env python tox --yes &&
micromamba run      --name neat_build_env pip install --extra-index-url https://test.pypi.org/simple/ --editable ".[test]" &&
micromamba run      --name neat_build_env tox run
```

# Build & Test Wheel on older python
```shell
micromamba create --name neat_test_env python=3.11 --yes  &&
(rm -f ./target/wheels/*.whl || true) &&
micromamba run --name neat_test_env  pip install ".[test]" &&
micromamba run --name neat_test_env  pytest
# micromamba run --name neat_test_env  pip wheel --wheel-dir ./target/wheels . &&
# micromamba run --name neat_test_env  pip install --ignore-installed ./target/wheels/*.whl &&
```

# Versioning Check
```shell
pip install setuptools-scm
python -m setuptools_scm
```