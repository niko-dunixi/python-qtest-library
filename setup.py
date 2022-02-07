# noinspection PyUnresolvedReferences
# https://stackoverflow.com/a/50314071/1478636
import setuptools
from distutils.core import setup

setup(
    name='qasymphony-qtest-library',
    version='0.2.2',
    packages=['qtest'],
    license='ISC',
    long_description=open('README.md').read(),
    long_description_content_type = 'text/markdown',
    install_requires=[
        'requests>=2.18.4',
    ],
    author='Paul N. Baker',
    author_email='paul.nelson.baker@gmail.com',
    url='https://github.com/paul-nelson-baker/python-qtest-library',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='qasymphony qtest quality-assurance qa',
    python_requires='~=3.6',
)
