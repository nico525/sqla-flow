from setuptools import setup

"""
0. python3 -m pip install --user --upgrade twine
1. python3 setup.py sdist bdist_wheel
2. python3 -m twine upload dist/*
see https://packaging.python.org/tutorials/packaging-projects/
"""

def requirements():
    import os
    filename = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    return [line.rstrip('\n') for line in open(filename).readlines()]

setup(name='sqla_flow',
      version='1.0.0',
      description='Workflow Mixin for SQLAlchemy',
      author='Nicolas Maier',
      author_email='info@nicolasmaier.de',
      license='MIT',
      packages=['sqla_flow'],
      zip_safe=False,
      include_package_data=True,
      keywords=['sqlalchemy', 'active record', 'activerecord', 'orm',
                'django-like', 'django', 'eager load', 'eagerload',  'repr',
                '__repr__', 'mysql', 'postgresql', 'pymysql', 'sqlite'],
      platforms='any',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Database',
      ]
  )