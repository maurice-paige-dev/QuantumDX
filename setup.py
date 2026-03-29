from setuptools import setup

setup(
    name='quantumdx',
    version='0.0.1',
    install_requires=[
        'requests',
        'importlib-metadata; python_version<"3.10"',
    ],
    packages=find_packages(
        # All keyword arguments below are optional:
        where='.',  # '.' by default
        include=['quantumdx*'],  # ['*'] by default
        exclude=['quantumdx.tests'],  # empty by default
    ),
)