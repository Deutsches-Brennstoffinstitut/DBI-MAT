from setuptools import setup

setup(
    name='dbimat',
    version='1.0.0',  # major.minor.patches
    packages=['dbimat',
              'dbimat.source',
              'dbimat.source.data',
              'dbimat.source.basic',
              'dbimat.source.helper',
              'dbimat.source.modules',
              'dbimat.source.model_base',
              'dbimat.source.model_base.Dataclasses'],
    url='https://gitea.dbi-gruppe.de/FG61-Modellierung/DBI_MAT',
    license='yes please',
    author='DBI-GTI',
    author_email='',
    description='Micro Grid Analysis Tool',
    install_requires=['pandas',
                      'openpyxl',
                      'numpy',
                      'scipy',
                      'strEnum',
                      'mysql',
                      'mysql-connector',
                      'CoolProp == 6.4.1',
                      'geopy',
                      'pvlib',
                      'joblib',
                      ],  # TODO: specify versions
    python_requires=">=3.8",
    package_data={'dbimat': ['dbimat\\source\\data\\dbi_mat.sqlite']}
)
