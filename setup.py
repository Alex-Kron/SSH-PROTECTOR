from setuptools import setup, find_packages

setup(
    name='sshprotect',
    version='0.0.3',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'paramiko',
    ],
    entry_points={
        'console_scripts': [
            'sshprotect = sshprotect.main:connect',
        ]
    },
)