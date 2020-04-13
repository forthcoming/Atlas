from web_demo import app

if __name__ == '__main__':
    print(app.url_map)
    app.run(host='127.0.0.1', port=1234)
