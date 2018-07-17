import setuptools

setuptools.setup(
    name = "Image reducer daemon",
    version = "0.0.1",
    author = "Hernan Yamakawa",
    author_email = "hernan.yamakawa@gmail.com",
    description = "A small python daemon to reduce images",
    install_requires = [
        'watchdog>=0.8.3,<0.9',
        'pylint>=1.9.2',
        'Pillow>=5.2.0,<5.3'
    ]
)