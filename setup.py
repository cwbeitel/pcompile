from setuptools import setup, find_packages

setup(
    name='pcompile',
    author='Christopher Beitel',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='BSD',
    keywords='autoprotocol',
    description=("A compiler for automated experimentation."),
    long_description=open('README.md').read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
        "Topic :: Scientific/Engineering",
        'Natural Language :: English',
    ],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'pcompile=pcompile.cli:cli',
        ]
    }
)
