# lippukala

App for managing e-tickets for conventions.

## Getting started

    python3 -m venv venv-lippukala
    source venv-lippukala/bin/activate

    git clone git@github.com:kcsry/lippukala
    cd lippukala
    pip install -e .[dev]

## POS test mode

    python lippukala_test_app.py seed
    python lippukala_test_app.py runserver
    start http://localhost:8000/pos

(Look at the `codes` JavaScript variable for example codes to use.)

## Copyright & license

    The MIT License (MIT)

    Copyright (c) 2013-2021 Aarni Koskela, Santtu Pajukanta

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
