import os
import tempfile

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(tempfile.gettempdir(), "lippukala_test.sqlite3"),
    }
}

SECRET_KEY = 'secret'

LIPPUKALA_PREFIXES = {
    "0": "mat",
    "1": "nom",
    "2": "dog-jono",
    "3": "cat-jono",
}

LIPPUKALA_LITERATE_KEYSPACES = {
    "0": "hopea kulta kumi lanka muovi nahka naru pahvi rauta teräs".split(),
    "1": "Aino Anna Armas Eino Elisabet Helmi Hilja Ilmari Johanna Johannes Juho Lauri Maria Martta Sofia Toivo Tyyne Vilho Väinö Yrjö".split(),
    "2": "Murre Rekku Haukku yksi pallo".split(),
    "3": "Miuku Mauku Kitler kaksi neliö".split(),
}

LIPPUKALA_CODE_MIN_N_DIGITS = 6
LIPPUKALA_CODE_MAX_N_DIGITS = 10

LIPPUKALA_PRINT_LOGO_PATH = "./fictitious_con.jpg"
LIPPUKALA_PRINT_LOGO_SIZE_CM = (5.84, 1.5)

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "lippukala",
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            'context_processors': (
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ),
        },
    },
]

ROOT_URLCONF = "lippukala_test_app.urls"
DEBUG = True
