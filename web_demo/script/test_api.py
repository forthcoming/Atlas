import requests
base_url='http://localhost:8080'
base_url='http://arerising.com:3456'
data={
    'category':'digital_office',
    'second':20,
}
r=requests.post('{}/ccktv/v1/test_celery/select'.format(base_url),data=data)
print(r.json())








