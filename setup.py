from pathlib import Path

from setuptools import setup

from bendy import version

release_version = version()

readme_path = Path(__file__).parent / "README.md"

with open(readme_path, encoding="utf-8") as f:
    long_description = f.read()

classifiers = [
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.11",
    "Typing :: Typed",
]

if "a" in release_version:
    classifiers.append("Development Status :: 3 - Alpha")
elif "b" in release_version:
    classifiers.append("Development Status :: 4 - Beta")
else:
    classifiers.append("Development Status :: 5 - Production/Stable")

classifiers.sort()

setup(
    author="Cariad Eccleston",
    author_email="cariad@cariad.earth",
    classifiers=classifiers,
    description="Bezier curve calculator",
    extras_require={
        "draw": [
            "pillow~=10.0",
        ],
    },
    include_package_data=True,
    install_requires=[
        "vecked~=1.6",
    ],
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="bendy",
    packages=[
        "bendy",
    ],
    package_data={
        "bendy": ["py.typed"],
    },
    python_requires=">=3.11",
    url="https://github.com/cariad/bendy",
    version=release_version,
)
