"prevent #-*- coding:utf-8 -*-"

from os import listdir, mkdir, rename, remove, makedirs, walk
from os.path import isfile, join, splitext, isdir, getsize
from shutil import disk_usage,rmtree,copy#remove not work if filled.rmtree(tempdir)

import json
from flask import send_from_directory, send_file, Response
from flask import Flask, render_template, request, jsonify, abort, redirect
import os

app = Flask(__name__)

#from tidyname import tidyName


#http://localhost:12800/newboard
@app.route('/')
def hello():
    return redirect( f"/in" )

@app.route('/in')
def iview():
    if request.method == "GET":
        #i = request.args.get('i')
        #mode = request.args.get('mode')        
        return render_template('first.html')

@app.route('/inf')
def ifview():
    if request.method == "GET":
        #i = request.args.get('i')
        #mode = request.args.get('mode')        
        return render_template('showtime.html')

import time

@app.route('/view', methods=['GET', 'POST'])
def fview():
    # data = { 'uploadkey': 'k', 'msg':'msgs' }
    # return jsonify(data)
    if request.method == 'POST':
        #name = request.form['name']
        #print(name,'na')
        
        #data = { 'uploadkey': 'k', 'msg':'msgs' }
        #data = requestdict['body']
        requestdict = request.get_json()
        data = requestdict
        tserver = int(time.time()*1000)
        
        data['dt']=tserver-requestdict['time']
        return jsonify(data)


@app.route('/static/<path:filenameinput>', methods=['GET', 'POST'])
def staticFile(filenameinput):
    return send_file( filename_or_fp = filenameinput )

if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0' , port = '12800')