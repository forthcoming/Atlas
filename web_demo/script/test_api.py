import requests
data={
    'category':'digital_office',
    'product_id':'540554959138',
}
r=requests.post('http://localhost:8080/ccktv/v1/test_celery/select',data=data)
print(r.json())
