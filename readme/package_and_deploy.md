


# Setup Editable Dev env
```shell
micromamba create   --name links_connect_build_env python --yes &&
micromamba run      --name links_connect_build_env pip install --extra-index-url https://test.pypi.org/simple/ --editable ".[test]" &&
micromamba run      --name links_connect_build_env tox run
```

# Install and Test on older python
```shell
micromamba create --name links_connect_test_env python=3.11 --yes  &&
micromamba run --name links_connect_test_env  pip install ".[test]" &&
micromamba run --name links_connect_test_env  pytest
```

# Build and Upload to TestPyPi using twine
* expects a `~/.pypirc` file with credentials for `testpypi` 
*  fails if the package is already uploaded, to generate new version add a commit which will increment the version number
```shell
micromamba create   --name links_connect_upload_testpypi_env python twine --yes &&
(rm -f ./target/wheels/*.whl || true) &&
micromamba run --name links_connect_upload_testpypi_env  pip wheel --wheel-dir ./target/wheels . &&
micromamba run --name links_connect_upload_testpypi_env  twine check ./target/wheels/*.whl &&
micromamba run --name links_connect_upload_testpypi_env  twine upload --repository testpypi ./target/wheels/*.whl
```

# Install from TestPyPi and Test
```shell
micromamba create   --name links_connect_install_testpypi_env  python pytest pytest-mock --yes &&
micromamba run      --name links_connect_install_testpypi_env  pip install --extra-index-url https://test.pypi.org/simple/ links_connect
micromamba run      --name links_connect_install_testpypi_env  pytest
```


# Versioning Check
```shell
pip install setuptools-scm
python -m setuptools_scm
```
