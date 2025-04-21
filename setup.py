import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='bt',
    version='0.1.0',
    author='Sarthak Chaudhary',
    author_email='sarthak.chaudhary46@gmail.com',
    description='A Python client for BeyondTrust Secret retrieval',
    long_description=open('readme.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/SarthakChaudhary46/BeyondTrust-Password-Fetch.git",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'urllib3'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
