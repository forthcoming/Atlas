from web_demo import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

    '''
    import requests
    data={
        'category':'digital_office',
        'product_id':'540554959138',
    }
    r=requests.post('http://localhost:5000/select',data=data)
    print(r.json())
    '''