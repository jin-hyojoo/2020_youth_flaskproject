import json

from flask import Flask, render_template, request, redirect, url_for, jsonify
from SearchBook import book_name, book_lib
from Location import calcdistance

app = Flask(__name__)

lib_list = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/result')
def result():
    return render_template('result.html')


@app.route('/list', methods=['POST'])
def list():
    global lib_list
    if request.method == 'GET':
        return render_template('result.html')
    else:
        idx = request.form['rec_key']
        data = lib_list[idx]
        return jsonify({"data": render_template('list.html', extra=data)})


@app.route('/search', methods=['GET', 'POST'])
def search():
    global lib_list
    bookname = request.form['bookname']
    author = request.form['author']
    latitude = float(request.form['latitude'])
    longitude = float(request.form['longitude'])

    #print(f'[DEBUG] book name is {bookname}')
    book_list = book_name(bookname, author)
    #print(f'[DEBUG] response code is {json.dumps(book_list, ensure_ascii=False, indent=4)}')
    lib_list_prev = book_lib(book_list)
    lib_list = calcdistance(lib_list_prev, latitude, longitude)
    #print(f'[DEBUG] library list is {json.dumps(lib_list, ensure_ascii=False, indent=4)}')

    if lib_list is None:
        return render_template('index.html', data=book_name)
    else:
        libdata = json.dumps(lib_list)
        libjson = json.loads(libdata)
        bookdata = json.dumps(book_list)
        bookjson = json.loads(bookdata)
        return render_template('result.html', lib=libjson, book=bookjson)


if __name__ == "__main__":
    app.run(debug=True)
