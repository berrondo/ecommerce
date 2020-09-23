[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/berrondo/ecommerce)

# ecommerce

## Como desenvolver?

1. Clone o repositório.
2. Crie um virtualenv com Python 3.8
3. Ative o virtualenv.
4. Instale as dependências
5. Configure a instância com o .env
6. Execute os testes.

```console
git clone git@github.com:berrondo/ecommerce.git ecommerce
cd ecommerce
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp contrib/env_sample .env
python manage.py test
```
