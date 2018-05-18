from distutils.core import setup

setup(
    name='QTestLibrary',
    version='0.2',
    packages=['qtest'],
    license='ISC',
    long_description=open('README.md').read(),
    install_requires=[
        'requests>=2.18.4',
    ],
)
