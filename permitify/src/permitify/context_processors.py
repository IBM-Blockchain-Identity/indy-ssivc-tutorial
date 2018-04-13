import os


def export_vars(request):
    data = {}
    data['THE_ORG_BOOK_APP_URL'] = os.environ.get('THE_ORG_BOOK_APP_URL')
    return data
