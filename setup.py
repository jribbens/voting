"""dispatches setuptools information."""

import setuptools


setuptools.setup(
    name="voting",
    version="0.0.1",
    description="UKVoting web systems",
    author="Jon Ribbens",
    author_email="jon-voting@unequivocal.co.uk",
    url="https://github.com/jribbens/voting",
    license="MIT",
    py_modules=["voting"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Framework :: Django :: 1.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
    ],
    install_requires=[
        "Django>=1.8",
        "dnspython3>=1.12",
    ]
)
