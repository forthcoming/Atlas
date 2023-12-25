import requests

base_url = 'http://localhost:1122'
data = {
    'category': 'digital_office',
    'second': 1,
}
r = requests.post('{}/ccktv/v1/test_celery/select'.format(base_url), data=data)
print(r.json())
