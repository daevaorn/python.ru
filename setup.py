#!/usr/bin/env python
import os

from distutils.core import setup


def files(dirname, strip='pythonru/'):
    return [os.path.join(base, f).split(strip)[1]
            for base, __, ff in os.walk(dirname, topdown=False)
            for f in ff]


setup(
    name='pythonru',
    version='0.1',
    packages=[
        'pythonru',
    ],

    package_data={
        'pythonru': (files('pythonru/templates')
                     + files('pythonru/static')
                     + files('pythonru/fixtures')),
    },

    author='Alex Koshelev',
    author_email='daevaorn@gmail.com',
    description='Python.ru site',
    url='https://github.com/daevaorn/python.ru',
)
