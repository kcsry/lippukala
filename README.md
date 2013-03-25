lippukala
=========

Seksiasuja ja kissoja

Getting started
---------------

    virtualenv --distribute venv-lippukala
    source venv-lippukala/bin/activate

    git clone git@github.com:kcsry/lippukala
    cd lippukala
    python setup.py develop

POS test mode
-------------

	python lippukala_test_app.py seed
	python lippukala_test_app.py runserver
	start http://localhost:8000/pos

(Look at the `codes` JavaScript variable for example codes to use.)