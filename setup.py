from setuptools import setup

setup(
    name='selmon',
    version='0.1',
    packages=['selmon','selmon.nagios'],
    url='https://github.com/objectified/selmon',
    install_requires=['selenium>=2.38.3', 'argparse>=1.2.1'],
    license='Apache License, 2.0',
    author='lbrouwer',
    author_email='objectified@gmail.com',
    description='Use Selenium Webdriver for Nagios monitoring',
    long_description='''
        This Python module facilitates writing Nagios plugins based on Selenium Webdriver,
        providing appropriate Nagios exit codes and performance data.''',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python',
    ],
)
