

```shell
micromamba create --name neat_build_env python --yes
```

```shell
micromamba create --name neat_build_env python --yes &&
micromamba run    --name neat_build_env pip install --extra-index-url https://test.pypi.org/simple/ -r requirements.txt
 
```

```shell
```