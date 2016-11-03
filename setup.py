from setuptools import setup
from setuptools import find_packages

package='kruemelmonster'

setup(
    name=package,
    version='0.0.2',
    author='Oz Tiram',
    author_email='oz.tiram@gmail.com',
    url='https://github.com/oz123/{}'.format(package),
    packages=find_packages(exclude=['tests']),
    license='LGPL',
    description='WSGI sessions implentation (session id in a cookie).',
    long_description=open('README.md').read(),
    platforms='any',
    download_url='http://pypi.python.org/pypi/{}/'.format(package),
)
