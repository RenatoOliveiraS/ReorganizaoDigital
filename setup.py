# setup.py
from setuptools import setup, find_packages

setup(
    name="meu_projeto",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    author="Seu Nome",
    description="Um exemplo simples do projeto Hello World",
    install_requires=[],  # Adicione suas dependências aqui
)
