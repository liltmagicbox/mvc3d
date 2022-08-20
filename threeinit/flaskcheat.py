"prevent #-*- coding:utf-8 -*-"

from os import listdir, mkdir, rename, remove, makedirs, walk
from os.path import isfile, join, splitext, isdir, getsize
from shutil import rmtree,copy#remove not work if filled.rmtree(tempdir)

from jar import getJar, imgtower_dir, jar_dir
import newdb
import userdb
from jsonio import *
import json
from flask import send_from_directory, send_file, Response
from flask import Flask, render_template, request, jsonify, abort, redirect

from resizer import justresize
app = Flask(__name__)

from tidyname import tidyName



@app.route('/')
def hello():
    #http://localhost:12800/newboard
    #boardList = list(newdb.db.keys())
    return redirect( "/view" )
    #return redirect( "/view?board="+boardList[0] )
    #return 'hello'


@app.route('/view')
def viewmain():
    backupcheck()
    if request.method == "GET":
        board = request.args.get('board')
        #print(board)works great!!!
        boardList = list(newdb.db.keys())

        if len(boardList)==0:
            return redirect( "/newboard" )

        allwriter = "none"
        hiddenboardList = []
        for b in boardList:
            if b.find('!') == 0:
                hiddenboardList.append( boardList.pop( boardList.index(b) ) )

        if board == None:
            board = boardList[0]
            headver = newdb.head[board][0]# .json script version.
            #board = "뉴보드5"#default view.
            return redirect( "/view?board="+board )
        else:
            if board.find('@') == 0:
                allwriter = "initial"

        headver = newdb.head[board][0]# .json script version.

        artistList = newdb.artistList[board]
        characterList = newdb.characterList[board]
        unitDict = newdb.unitDict[board]
    return render_template('rocketbox.html', boardList=boardList, board = board, headver = headver,
    hiddenboardList=hiddenboardList, allwriter=allwriter,
    artistList=artistList, characterList=characterList, unitDict=unitDict )

@app.route('/taginput')
def taginput():
    if request.method == "GET":
        boardList = list(newdb.db.keys())
        board = request.args.get('board')
        if board == None:
            board = boardList[0]
            return redirect( "/taginput?board={}".format(board) )
        headver = newdb.head[board][0]# .json script version.

        characterList = newdb.characterList[board]
        unitDict = newdb.unitDict[board]
    return render_template('highspeedtag.html' , board = board, headver = headver, boardList=boardList, characterList=characterList, unitDict=unitDict)

@app.route('/server_info')
def hello_json():
    data = {'server_name' : '0.0.0.0', 'server_port' : '8080'}
    return jsonify(data)




@app.route('/jarscan')
def jarScan():
    global datas
    no = backupDatas(datas)
    datas = minidb.jarScan(datas)
    return "backup no:"+str(no)+'jarscan after:'+str(len(datas))

# @app.route('/file/<path:filenameinput>', methods=['GET', 'POST'])
# def download(filenameinput):
#     # 디렉터리에선 폴더명이다. upload 로 s안붙이니 안나왔음;
#     #파일네임을 입력을 받은걸, 어떻게든 넘기는구조같다.
#     #디렉터리에서 파일을 보내는 함수라는것은 알겠어..
#     return send_from_directory(directory='uploads', filename=filenameinput)




#used /static/js/---.js or so.
@app.route('/static/<path:filenameinput>', methods=['GET', 'POST'])
def staticFile(filenameinput):
    # 디렉터리에선 폴더명이다. upload 로 s안붙이니 안나왔음;
    #파일네임을 입력을 받은걸, 어떻게든 넘기는구조같다.
    #디렉터리에서 파일을 보내는 함수라는것은 알겠어..
    #print('filenameinput',filenameinput)
    #return send_file( filename=filenameinput )
    return send_file( filename_or_fp = filenameinput )
    #http://localhost:12800/static/mah.txt로 접속시,staic폴더안에연결됨.ㅇㅋ




#------------------------ fetch

#toolong @app.route('/fetch/bodytext/<path:no>')
@app.route('/fetch')
def fetchParse():
    global datas
    no = request.args.get('no')
    key = request.args.get('key')
    #request.query_string
    ##print(no,key)
    valueText = datas[no][key]
    ##print(valueText)
    #return( valueText )
    #data = {'server_name' : '0.0.0.0', 'server_port' : '8080'}# it! works!
    data = { 'bodytext':valueText }
    return jsonify(data)

@app.route('/heavyfetch')
def heavyfetchParse():
    global datas
    global fluid
    #no = request.args.get('no')
    key = request.args.get('key')
    #request.query_string
    tmplist=[]
    tmplist2=[]
    tmpdict={}
    for n in fluid:
        tmpdict[n] = fluid[n][key]

    valueText = datas[no][key]
    print(no,key)
    print(valueText)
    #return( valueText )
    #data = {'server_name' : '0.0.0.0', 'server_port' : '8080'}# it! works!
    data = { 'bodytext':valueText }
    return jsonify(data)

# @app.route('/bodyload')
# def bodyload():
#     global datas
#     global fluid
#     key = request.args.get('key')
#     tmpdict[n] = fluid[n][key]
#     data = { 'bodytext':valueText }
#     return jsonify(data)

@app.route('/fetchbodytext')
def fetchbodytext():
    board = request.args.get('board')
    no = request.args.get('no')
    #key = request.args.get('key')
    key = newdb.body_key#more specific.

    #request.query_string
    ##print(no,key)
    valueText = newdb.db[board][no][key]
    ##print(valueText)
    #return( valueText )
    #data = {'server_name' : '0.0.0.0', 'server_port' : '8080'}# it! works!
    #return valueText

    time = datestr()
    newdb.add_view(board,no, time, 'noname')#fine view ++ button may abuse.


    data = { 'bodytext':valueText }
    return jsonify(data)



#이거보단명령어.ㅇㅋ. fluiddb.fluid[no]['캐릭터태그']

tdict={}
@app.route('/fetchtag'  , methods = ['POST'])
def fetchtag():
    global tdict
    #print(request.query_string)

    requestdict = request.get_json()
    token = requestdict['token']
    board = requestdict['board']
    id = requestdict['id']
    taglist = requestdict['taglist']
    #print(requestdict)
    #print(taglist)
    #print('seenow')

    # token = request.args.get('token')
    # board = request.args.get('board')
    # id = request.args.get('id')
    # taglist = request.args.get('taglist')
    #taglist = taglist.split(',')
    #tdict[id]=taglist
    #taglist = list(set(taglist))

    id=str(id)
    username = userdb.getname(token)
    if username == "noname":
        abort(403)#403 Forbidden

    time = datestr()
    key = newdb.tag_key
    #newdb.db[board][id][key] = {}

    for text in taglist:
        if text == "":
            pass
        userinfo = newdb.setuserinfo(time,username,text, see = newdb.see_default)
        newdb.add(board,id,key,userinfo)

    # if fluiddb.fluidset(no) == True:#made this time.
    #     for text in taglist:
    #         if fluiddb.addtext(user,no,key,text) != True:
    #             print('NEVER SEE THIS error but exception it exit.bad!')
    #         else:
    #             print('add first ok')
    # else:#alreadywas. rewrite
    #     fluiddb.cleartext(user,no,key,)
    #
    #         #print('subtext', fluiddb.subtext(user,no,key,text) )
    #         #print('addagain', fluiddb.addtext(user,no,key,text) )
    # #fluiddb.addn(user,no,'조')
    # print(no,taglist)
    #return newdb.db[board][id][key]

    return "1"






def clearjar():
    pass

#----------------------upload
from timemaker import millisec, datestr, intsec, datestrstamp, daystr
from uuid import uuid4
#-------lock jar.
# user, time, remainT, key(secret)
jarinfo = ["",0,0,""]


def isfreejar():
    global jarinfo
    if jarinfo[2]-intsec()<0:
        unlockjar()
    return jarinfo[0] == ""

def lockjar(username):
    global jarinfo
    jarinfo[0] = username
    jarinfo[1] = intsec()
    jarinfo[2] = jarinfo[1]+30
    jarinfo[3] = str(uuid4())[:13]
    return jarinfo[3]

def unlockjar():
    global jarinfo
    jarinfo[0] = ""
    jarinfo[1] = intsec()
    jarinfo[3] = ""

# def authjar(username):
#     global jarinfo
#     return jarinfo[0] == username

def jaraddtime(size):
    global jarinfo
    jarinfo[2] += int(float(size)*3.4) #1000MB, 2000sec... to 3...to 3.4

def keycheck(uploadkey):
    return jarinfo[3]==uploadkey

def getuploadkey(username):
    if isfreejar() == True:
        return lockjar(username)
    else:
        return ""

#this can be bad by js change.
# @app.route('/lockjar', methods = [ 'POST'])
# def lockjar():
#     global jarinfo
#     if jarinfo[0] == "":
#         token = request.form['token']
#         username = userdb.getname(token)
#         if username == "noname":
#             "only logged in."
#         jarinfo[0] = username
#         jarinfo[1] = datestr()
#         return "jar in"
#     else:
#         return "jar busy! by {}, from {}".format(jarinfo[0],jarinfo[1])
#
# @app.route('/unlockjar', methods = [ 'POST'])
# def unlockjar():
#     global jarinfo
#     token = request.form['token']
#     username = userdb.getname(token)
#     if username == jarinfo[0]:
#         jarinfo[0] == ""
#     jarinfo[1] = datestr()



@app.route('/uploadkey', methods = [ 'POST'])
def uploadkey():
    if request.method == 'POST':
        token = request.form['token']
        board = request.form['board']

        username = userdb.getname(token)
        if username == "noname":
            #abort(403)#403 Forbidden
            #익명
            if board.find('@') == 0:
                1
            else:
                abort(403)#403 Forbidden

        #---jar auth.
        uploadkey = getuploadkey(username)
        if uploadkey == "":
            msg = "jar busy! by {}, from {}, remain time: {}".format(jarinfo[0], datestrstamp(jarinfo[1]), (jarinfo[2]-intsec()) )
        else:
            msg = ""

        data = { 'uploadkey': uploadkey, 'msg':msg }
        return jsonify(data)

import zipfile
import zipfileuni
from werkzeug.utils import secure_filename
#업로드 HTML 렌더링
# @app.route('/upload')
# def render_file():
#     boardList = list(newdb.db.keys())
#     return render_template('filedrop.html', galleryList = boardList )


#@app.route('/upload/<path:boardname>', methods=['GET'])
@app.route('/upload', methods=['GET'])
def render_file():
    boardname = request.args.get('boardname')
    #print(boardname)
    galleryList = [boardname]
    return render_template('filedrop.html', galleryList = galleryList)

# @app.route('/smallupload')
# def render_file_small():
#     boardList = list(newdb.db.keys())
#     return render_template('smalldrop.html', galleryList = boardList )

#파일 업로드 처리
#https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
@app.route('/zipfileup', methods = [ 'POST'])
def zipfileup():
    if request.method == 'POST':
        board = request.form['board']
        ziptype = request.form['ziptype']
        zipsize = request.form['zipsize']#for jaresti(size)

        upload_key = request.form['upload_key']
        print(zipsize)
        print(keycheck(upload_key) )
        if keycheck(upload_key) == False: abort(403)#403 Forbidden

        if not board in newdb.db.keys():
            abort(403)#403 Forbidden
        if float(zipsize)>5000:
            abort(403)#403 Forbidden


        f = request.files['file']
        #f.save(secure_filename(f.filename))
        #print(f.filename)
        if f.filename[-3:] != 'zip':
            abort(403)#403 Forbidden
        #sname = secure_filename(f.filename)
        sname = tidyName(f.filename)
        #print(sname)

        if ziptype=="단일만화":#manga
            fname = splitext(sname)[0]
            unzipdir = join(jar_dir,fname)
            mkdir( unzipdir)
        elif ziptype == "여러개묶음":#novels, imgs, crawl
            unzipdir = jar_dir


        filepath = join(unzipdir,sname)
        f.save( filepath )
        size = getsize( filepath )//1024//1024#xMB.
        if size>5000:
            remove(filepath)# need log here.
            abort(403)#403 Forbidden

        jaraddtime(size)
        zf = zipfileuni.ZipFile( filepath )
        zf.extractall(unzipdir)
        zf.close()
        remove(filepath)

        newdict,jarerrlist = getJar( newdb.db[board] )
        errstr = ""
        for i in jarerrlist:
            errstr+=i
            errstr+="\n"

        #board = board
        uploader = jarinfo[0]
        uploadtime = datestr()
        for id in newdict:
            #----------------------for custom dict additional option
            #del only [번역]---.
            if newdict[id]['제목'].startswith('[번역]'):
                newdict[id]['제목'] = newdict[id]['제목'].split('[번역]')[1].strip()
            #if '센세)', add 태그.
            tagtext = ""#for tag exist.
            if newdict[id]['제목'].find('센세)') != -1 :
                #tagtext = '작가:'+newdict[id]['제목'].split('센세)')[0].strip()
                tagtext = newdict[id]['제목'].split('센세)')[0].strip()
                newdict[id]['제목'] = newdict[id]['제목'].split('센세)')[1].strip()

            #-general work
            if newdict[id].get(newdb.date_key) == None:
                newdict[id][newdb.date_key] = daystr()

            newdb.newarticle(board,id,uploader,uploadtime)
            newdb.db[board][id].update( newdict[id] )

            #post-custom additonal option..it caused err!
            if tagtext != "":
                newdb.addtag(board,id, uploadtime,uploader,tagtext )

        #get headdict, backup.
        newdb.after_newarticle(board)#backupinside
        newdb.lastbackuptime = intsec()

        unlockjar()
        zipdonetext = "success:{}, err:{}, errmsg:{}".format( len(newdict), len(jarerrlist), errstr )
        return zipdonetext
        #return str(newdict)+str(jarerrlist)
        #return '처리완료:{},{}MB <br>이전 목록 길이:{} <br> {}'.format(sname,size,oldlen,scann)


# @app.route('/rawfileup', methods = [ 'POST'])
# def rawfileup():
#     if request.method == 'POST':
#         board = request.form['board']
#
#         f = request.files['file']
#         if f.filename[-3:] != 'zip':
#             return 'zip파일을 줘!'
#         sname = secure_filename(f.filename)
#         fname = splitext(sname)[0]
#         unzipdir = join(jar_dir,fname)
#         mkdir( unzipdir)
#         filepath = join(unzipdir,sname)
#         f.save( filepath )
#         size = getsize( filepath )//1024//1024
#         zf = zipfile.ZipFile( filepath )
#         zf.extractall(unzipdir)
#         zf.close()
#         return "done"



#------------------------ post file upload.


@app.route("/xmliterimg", methods=['POST'])
def xmliterimg():
    f = request.files['file']
    #js cuts 20MB, but if 100MB comes, can't block!
    # pointer gose end, cant save img!
    if 'mp4' in f.filename or 'mkv' in f.filename:
        1
        #print('mp4 mkv')
        #f.seek(0)
    else:
        blob = f.read()
        fsize = len(blob)
        if fsize < 25014825:#25MB,8digits.
            #print('not video but smallsize')
            f.seek(0)
    iter = request.form['iter']
    #print(f)
    #print(iter)
    upload_key = request.form['upload_key']
    if keycheck(upload_key) == False: abort(403)#403 Forbidden

    #--------make dir
    titletext = request.form['titletext']
    if titletext == "":titletext = "no title"
    titletext = titletext[:30]
    sname = tidyName(titletext)
    unzipdir = join(jar_dir,sname)
    makedirs(unzipdir, exist_ok=True)

    ext = splitext(f.filename)[1]
    sname =  iter+ext
    #sname = secure_filename(f.filename)
    filepath = join(unzipdir,sname)
    jaraddtime(7)#5 to 7.. if 10mb.
    f.save( filepath )
    return "imgup"#it's key to tell success! see filedrop.html

@app.route("/xmltext", methods=['POST'])
def xmltext():
    board = request.form['board']
    #uploader = request.form['username']
    bodytext = request.form['bodytext']

    upload_key = request.form['upload_key']
    #print(upload_key) #note that if same tab, fast clicked, it fails. by new key.
    if keycheck(upload_key) == False: abort(403)#403 Forbidden

    #--------make dir
    titletext = request.form['titletext']
    if titletext == "":titletext = "no title"
    titletext = titletext[:30]
    sname = tidyName(titletext)
    unzipdir = join(jar_dir,sname)
    makedirs(unzipdir, exist_ok=True)

    #print(1) if 1==2 else print(2)
    txtname = join(unzipdir,"body.txt")
    with open ( txtname, 'w', encoding = "utf-8") as f:
        f.write(bodytext)

    #---get jar seq.
    newdict,jarerrlist = getJar( newdb.db[board] )
    errstr = ""
    for i in jarerrlist:
        errstr+=i
        errstr+="\n"

    #board = board
    uploader = jarinfo[0]
    uploadtime = datestr()
    for id in newdict:
        if newdict[id].get(newdb.date_key) == None:
            newdict[id][newdb.date_key] = daystr()

        newdb.newarticle(board,id,uploader,uploadtime)
        newdb.db[board][id].update( newdict[id] )

    newdb.after_newarticle(board)

    unlockjar()
    #return "txtup"#it's key to tell success! see filedrop.html
    textdonetext = "success:{}, err:{}, errmsg:{}".format( len(newdict), len(jarerrlist), errstr )
    return textdonetext


#-----------------------------new board.
#
# @app.route('/parent', methods=['GET', 'POST'])
# def parent():
#     return render_template('htmlparent.html')

@app.route('/son', methods=['GET', 'POST'])
def son():
    a={}
    a['age']=3
    return render_template('son.html' , ob=a)


@app.route('/newboard', methods=['GET', 'POST'])
def newboard():
    return render_template('newboard.html')

@app.route('/createboard', methods=['GET', 'POST'])
def createboard():
    if request.method == 'POST':
        token = request.form['token']
        username = userdb.getname(token)
        if username == "noname":
            return "you can not make it!"
        if userdb.ismanager(username) or userdb.ismaster(username):
            pass
        else:
            return "noauth"

        name = request.form['name']
        #----------json save * error. why??
        #if name.find('*') != -1:
        #    name = 'x'.join( name.split('*') )
        #for dir headjson, banner error.
        name = tidyName(name)
        name = name.replace(' ','_')#for options.value.

        #boardtype = request.form['boardtype']
        #heros = request.form['heros']2020.12.07.
        if newdb.newboard(name) == True:#backup inside.
            newdb.lastbackuptime = intsec()
            return "new board created : {}".format(name)
        else:
            return " board already! "


#제목하고 작성자,업로더 등 비밀스런 풀정보 다 공개하기.. 및 수정,삭제모드.
#정렬은 솔직히 하기 싫은데요..

# @app.route('/articleboard' )
# def articleboard():
#     dataList = []
#     board = "gallery"
#     for id in newdb.db[board]:
#         item = {}
#         item["id"] = newdb.db[board][id][newdb.id_key]
#         item["title"] = newdb.db[board][id][newdb.title_key]
#         item["writer"] = newdb.db[board][id][newdb.writer_key]
#         item["date"] = newdb.db[board][id][newdb.date_key]
#
#         item["uploadtime"] = newdb.db[board][id].get(newdb.uploadtime_key)
#         item["uploader"] = newdb.db[board][id].get(newdb.uploader_key)
#
#         dataList.append( item )
#
#         boardList = list(newdb.db.keys())
#     #return render_template('articleboard.html' ,dataList = dataList, boardList = boardList)

@app.route('/manageboard' )
def boardmanager():
    boardList = list(newdb.db.keys())
    return render_template('manageboard.html' , boardList = boardList)

@app.route('/xmltaginfos', methods=[ 'POST'])
def xmltaginfos():
    if request.method == 'POST':
        boardname = request.form['boardname']
        d={}
        d["artistList"]=newdb.artistList[boardname]
        d["characterList"]=newdb.characterList[boardname]
        d["unitDict"]=newdb.unitDict[boardname]

        d["charC"]=newdb.charC[boardname]
        d["unitC"]=newdb.unitC[boardname]
        return jsonify(d)

@app.route('/xmlcharC', methods=[ 'POST'])
def xmlcharC():
    if request.method == 'POST':
        bstate = request.form['bstate']
        boardname = request.form['boardname']
        charC = request.form['charC']
        charC = json.loads(charC)

        token = request.form['token']
        username = userdb.getname(token)
        if username == "noname":
            return "you can not make it!"
        if userdb.ismanager(username) or userdb.ismaster(username):
            pass
        else:
            return "you can not make it!"

        if bstate == "B":#for button color.
            bodytext = ""
            for key,val in charC.items():
                bodytext+=".tagB_character[name ="+key+"]{border-color: "+val+"}"
                bodytext+="\n"
            dirpath = join('static','css')
            makedirs(dirpath, exist_ok=True)
            unitname= 'charcolor_{}.css'.format(boardname)
            txtname = join(dirpath,unitname)

            with open ( txtname, 'w', encoding = "utf-8") as f:
                f.write(bodytext)
            newdb.charC[boardname] = charC

        if bstate == "BB":#for unit board color.
            bodytext = ""
            for key,val in charC.items():
                if type(val)==str:
                    bodytext+=".imgFrame .imgBox[color ="+key+"]{background-color: "+val+"}"
                    bodytext+="\n"
                elif type(val)==list:
                    if len(val)==2:
                        val,val2 = val
                        bodytext+=".imgFrame .imgBox[color ="+key+"]{background: linear-gradient(112deg, "+val+" 23%, "+val2+" 77%);}"
                    elif len(val)==3:
                        val,val2,val3=val
                        bodytext+=".imgFrame .imgBox[color ="+key+"]{background: linear-gradient(112deg, "+val+" 15%, "+val2+" 50%,"+val3+" 80%);}"
                    elif len(val)==4:
                        val,val2,val3,val4=val
                        bodytext+=".imgFrame .imgBox[color ="+key+"]{background: linear-gradient(112deg, "+val+" 10%, "+val2+" 30%,"+val3+" 70%,"+val4+" 90%);}"
                    else:
                        bodytext+=".imgFrame .imgBox[color ="+key+"]{background-color: "+val[0]+"}"
                    bodytext+="\n"
            dirpath = join('static','css')
            makedirs(dirpath, exist_ok=True)
            unitname= 'unitcolor_{}.css'.format(boardname)
            txtname = join(dirpath,unitname)

            with open ( txtname, 'w', encoding = "utf-8") as f:
                f.write(bodytext)
            newdb.unitC[boardname] = charC

        #xmlbackup
        return "done"

@app.route('/xmladdtaginfo', methods=[ 'POST'])
def xmladdtaginfo():
    if request.method == 'POST':
        artists = request.form['artists']
        characters = request.form['characters']
        #units = request.form['units']
        unitjson = request.form['unitjson']

        board = request.form['boardname']

        token = request.form['token']
        username = userdb.getname(token)
        if username == "noname":
            return "you can not make it!"
        if userdb.ismanager(username) or userdb.ismaster(username):
            pass
        else:
            return "you can not make it!"

        unitdict = json.loads(unitjson)
        for i in unitdict:
            unitdict[i] = unitdict[i].split()

        newdb.artistList[board].extend(artists.split())
        newdb.characterList[board].extend(characters.split())
        newdb.artistList[board] = list(set( newdb.artistList[board] ))
        newdb.characterList[board] = list(set( newdb.characterList[board] ))

        newdb.unitDict[board].update(unitdict)
        #xmlbackup
        return "ok"

@app.route('/xmldeltaginfo' , methods = ['POST'] )
def xmldeltaginfo():
    listname = request.form['listname']
    board = request.form['board']
    tagname = request.form['tagname']

    token = request.form['token']
    username = userdb.getname(token)
    if username == "noname":
        return "noname"

    if userdb.ismanager(username) or userdb.ismaster(username):
        pass
    else:
        return "noname"

    if listname == "artistList":
        for i in newdb.artistList[board]:
            if i == tagname:
                newdb.artistList[board].remove(i)
    if listname == "characterList":
        for i in newdb.characterList[board]:
            if i == tagname:
                newdb.characterList[board].remove(i)

    if listname == "unitDict":
        del newdb.unitDict[board][tagname]
    #xmlbackup
    return "done"


@app.route('/xmltagcopy' , methods = ['POST'] )
def xmltagcopy():
    board = request.form['board']
    newboard = request.form['newboard']

    token = request.form['token']
    username = userdb.getname(token)
    if username == "noname":
        return "noname"

    if userdb.ismanager(username) or userdb.ismaster(username):
        pass
    else:
        return "noname"

    newdb.unitC[newboard] = newdb.unitC[board]
    newdb.charC[newboard] = newdb.charC[board]
    newdb.artistList[newboard] = newdb.artistList[board]
    newdb.characterList[newboard] = newdb.characterList[board]
    newdb.unitDict[newboard] = newdb.unitDict[board]
    #xmlbackup
    #--------------------------------
    board = tidyName(board)
    newboard = tidyName(newboard)
    newboardpath = join('static','banner',newboard)
    try:
        rmtree(newboardpath)
    except:
        pass
    makedirs(newboardpath, exist_ok=True)

    boardpath = join('static','banner',board)
    for f in listdir(boardpath):
        boardpathf = join(boardpath,f)
        newpathf = join(newboardpath,f)
        copy(boardpathf,newpathf)

    return "done"

@app.route('/xmlbannerup' , methods = ['POST'] )
def xmlbannerup():
    f = request.files['img']
    board = request.form['board']
    unitname = request.form['unitname']

    token = request.form['token']
    username = userdb.getname(token)
    if username == "noname":
        return "noname"

    if userdb.ismanager(username) or userdb.ismaster(username):
        pass
    else:
        return "noname"

    board = tidyName(board)
    unitname = tidyName(unitname)

    dirpath = join('static','banner',board)
    makedirs(dirpath, exist_ok=True)

    unitname= unitname+'.png'
    filepath = join(dirpath,unitname)
    f.save( filepath )
    w,h = (500,281)
    if justresize(filepath,w,h):
        return "done"
@app.route('/xmlcssup' , methods = ['POST'] )
def xmlcssup():
    f = request.files['img']
    board = request.form['board']

    token = request.form['token']
    username = userdb.getname(token)
    if username == "noname":
        return "noname"

    if userdb.ismanager(username) or userdb.ismaster(username):
        pass
    else:
        return "noname"

    board = tidyName(board)

    dirpath = join('static','css')
    makedirs(dirpath, exist_ok=True)

    unitname= 'unitcolor.css'
    filepath = join(dirpath,unitname)
    f.save( filepath )
    return "done"

@app.route('/articleboard' )
def articleboard():
    boardList = list(newdb.db.keys())
    userList = list(userdb.user.keys())
    return render_template('articleboard.html', boardList = boardList, userList = userList)

@app.route('/articleboarduser' ,methods=['GET', 'POST'] )
def articleboarduser():
    boardList = []
    for board in list(newdb.db.keys()):
        if board.find('@')==0:
            boardList.append(board)
    return render_template('articleboarduser.html', boardList = boardList)


@app.route('/articleview' , methods=['GET'])
def articleview():
    board = request.args.get('board')
    user = request.args.get('user')
    key = request.args.get('key')

    dataList=[]
    if user =="모든유저" and key == "글":
        for id in newdb.db[board]:
            item = {}
            item["id"] = newdb.db[board][id][newdb.id_key]
            item["title"] = newdb.db[board][id][newdb.title_key]
            item["writer"] = newdb.db[board][id][newdb.writer_key]
            item["date"] = newdb.db[board][id][newdb.date_key]

            item["uploadtime"] = newdb.db[board][id].get(newdb.uploadtime_key)
            item["uploader"] = newdb.db[board][id].get(newdb.uploader_key)

            dataList.append( item )

    elif user !="모든유저" and key == "글":
        for id in newdb.db[board]:
            if newdb.db[board][id].get(newdb.uploader_key)== user:
                item = {}
                item["id"] = newdb.db[board][id][newdb.id_key]
                item["title"] = newdb.db[board][id][newdb.title_key]
                item["writer"] = newdb.db[board][id][newdb.writer_key]
                item["date"] = newdb.db[board][id][newdb.date_key]
                item["uploadtime"] = newdb.db[board][id].get(newdb.uploadtime_key)
                item["uploader"] = newdb.db[board][id].get(newdb.uploader_key)
                dataList.append( item )
    elif user !="모든유저" and key == "좋아":
        for id in newdb.db[board]:
            for i in newdb.db[board][id][newdb.like_key]:
                if newdb.db[board][id][newdb.like_key][i][newdb.user_key] == user:
                    #print('haha')
                    item = {}
                    item["id"] = newdb.db[board][id][newdb.id_key]
                    item["title"] = newdb.db[board][id][newdb.title_key]
                    item["writer"] = newdb.db[board][id][newdb.writer_key]
                    item["date"] = newdb.db[board][id][newdb.date_key]
                    item["uploadtime"] = newdb.db[board][id].get(newdb.uploadtime_key)
                    item["uploader"] = newdb.db[board][id].get(newdb.uploader_key)
                    dataList.append( item )
    elif user !="모든유저" and key == "추천":
        for id in newdb.db[board]:
            for i in newdb.db[board][id][newdb.recom_key]:
                if newdb.db[board][id][newdb.recom_key][i][newdb.user_key] == user:
                    item = {}
                    item["id"] = newdb.db[board][id][newdb.id_key]
                    item["title"] = newdb.db[board][id][newdb.title_key]
                    item["writer"] = newdb.db[board][id][newdb.writer_key]
                    item["date"] = newdb.db[board][id][newdb.date_key]
                    item["uploadtime"] = newdb.db[board][id].get(newdb.uploadtime_key)
                    item["uploader"] = newdb.db[board][id].get(newdb.uploader_key)
                    dataList.append( item )

    elif user !="모든유저" and key == "태그":
        for id in newdb.db[board]:
            for i in newdb.db[board][id][newdb.tag_key]:
                if newdb.db[board][id][newdb.tag_key][i][newdb.user_key] == user:
                    item = {}
                    item["id"] = newdb.db[board][id][newdb.id_key]
                    item["title"] = newdb.db[board][id][newdb.title_key]
                    item["writer"] = newdb.db[board][id][newdb.writer_key]
                    item["date"] = newdb.db[board][id][newdb.date_key]
                    item["uploadtime"] = newdb.db[board][id].get(newdb.uploadtime_key)
                    item["uploader"] = newdb.db[board][id].get(newdb.uploader_key)
                    item["text"] = newdb.db[board][id][newdb.tag_key][i][newdb.text_key]
                    item["idx"] = i
                    item["type"] = "태그"
                    dataList.append( item )
    elif user !="모든유저" and key == "댓글":
        for id in newdb.db[board]:
            for i in newdb.db[board][id][newdb.comm_key]:
                if newdb.db[board][id][newdb.comm_key][i][newdb.user_key] == user:
                    item = {}
                    item["id"] = newdb.db[board][id][newdb.id_key]
                    item["title"] = newdb.db[board][id][newdb.title_key]
                    item["writer"] = newdb.db[board][id][newdb.writer_key]
                    item["date"] = newdb.db[board][id][newdb.date_key]
                    item["uploadtime"] = newdb.db[board][id].get(newdb.uploadtime_key)
                    item["uploader"] = newdb.db[board][id].get(newdb.uploader_key)
                    item["text"] = newdb.db[board][id][newdb.comm_key][i][newdb.text_key]
                    item["idx"] = i
                    item["type"] = "댓글"
                    dataList.append( item )


    sortedList = sorted( dataList , key= lambda k: k["uploadtime"]  ,reverse = True)#higher first
    return render_template('articleviewer.html' , boardname = board, itemList = sortedList)


# @app.route('/Fshowarticles' , methods = ['POST'] )
# def Fshowarticles():
#     requestdict = request.get_json()
#     board = requestdict['board']
#     print(board)
#
#     dataList=[]
#     for id in newdb.db[board]:
#         item = {}
#         item["id"] = newdb.db[board][id][newdb.id_key]
#         item["title"] = newdb.db[board][id][newdb.title_key]
#         item["writer"] = newdb.db[board][id][newdb.writer_key]
#         item["date"] = newdb.db[board][id][newdb.date_key]
#
#         item["uploadtime"] = newdb.db[board][id].get(newdb.uploadtime_key)
#         item["uploader"] = newdb.db[board][id].get(newdb.uploader_key)
#
#         dataList.append( item )
#
#     return jsonify(dataList)


@app.route('/xmldelarticle' , methods = ['POST'] )
def xmldelarticle():
    board = request.form['board']
    id = request.form['id']
    token = request.form['token']

    username = userdb.getname(token)

    #writer = newdb.db[board][id][newdb.writer_key] #this, original writer,,toobad!
    writer =newdb.db[board][id][newdb.uploader_key]
    if username != writer:
        if userdb.ismanager(username) or userdb.ismaster(username):
            pass
        else:
            return "noname"

    if subarticle(board,id) == True:
        text = "del success!"
        xmlbackup()
        #xmlbackup
    else:
        text = "del fail.."
    return text

@app.route('/fetchdelarticle' , methods = ['POST'] )
def fetchdelarticle():
    requestdict = request.get_json()
    board = requestdict['board']
    id = requestdict['id']
    if subarticle(board,id) == True:
        text = "sub success!"
    else:
        text = "sub fail.."
    data={"text" : text}
    return jsonify(data)

@app.route('/xmlmodtitle' , methods = ['POST'] )
def xmlmodtitle():
    board = request.form['board']
    id = request.form['id']
    token = request.form['token']
    newtitle = request.form['newtitle']

    username = userdb.getname(token)

    if userdb.ismanager(username) or userdb.ismaster(username):
        pass
    else:
        return "you can not delete!"

    newdb.db[board][id][newdb.title_key] = newtitle
    text = "mod success!"
    xmlbackup()
    #xmlbackup
    return text

#x버튼에연계, post로 들어오면,제거하기.?
def subarticle(board,id):
    newdb.subarticle(board,id)
    subimgs(id)
    return True

def subimgs(id):
    try:
        rmtree( join(imgtower_dir, id) )
    except FileNotFoundError:
        pass

# too tricky, even imgtower. we do not prevent from now.!
#def getpreventset():
#    newdb.db[board][id]

@app.route('/delboard' )
def delboard():
    boardList = list(newdb.db.keys())
    return render_template('delboard.html' , boardList = boardList)

@app.route('/delboardname' ,methods = ["POST"])
def delboardname():
    board = request.form['board']
    token = request.form['token']

    username = userdb.getname(token)
    if username == "noname":
        return "you can not make it!"
    #if userdb.ismanager(username) or userdb.ismaster(username):
    #only master can del!
    if userdb.ismaster(username):
        pass
    else:
        return "noauth"

    if delboard(board) == True:
        xmlbackup()
        #xmlbackup
        return "del board done : {}".format(board)
    else:
        return " error.. anyway."

def delboard(board):#sincefile..not int newdb.
    if newdb.db.get(board) != None:
        for id in newdb.db[board]:
            try:rmtree(join(imgtower_dir, id))
            except:pass
        try:rmtree(join('static','banner',board))
        except:pass
        del newdb.db[board]
        newdb.deltaginfo(board)
        del newdb.charC[board]
        del newdb.unitC[board]
        return True
    return False

#--------------------------user methods

@app.route('/assignuser' )
def assignuser():
    masterList = userdb.masters
    managerList = userdb.managers
    userList = list(userdb.user.keys())
    return render_template('assignuser.html', masterList=masterList, managerList=managerList, userList = userList)

@app.route('/assignauth', methods = [ 'POST'] )
def assignauth():
    token = request.form['token']
    username = userdb.getname(token)
    if username == "noname":
        return "noname"
    if userdb.ismaster(username):
        pass
    else:
        return "noauth"

    name = request.form['name']
    auth = request.form['auth']
    if auth == "master":
        return userdb.newmaster(name)
    elif auth == "manager":
        return userdb.newmanager(name)
    elif auth == "user":
        return userdb.normaluser(name)
    elif auth == "delete":
        return userdb.deluser(name)
    return "badgateway"


@app.route('/newuserpage' )
def newuserpage():
    return render_template('newuserpage.html')

@app.route('/newuser' , methods = [ 'POST'])#why need get?
def newuser():
    if request.method == 'POST':
        username = request.form['username']
        sha = request.form['sha']
        return userdb.newuser(username,sha)

@app.route('/login' , methods = [ 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        sha = request.form['sha']
        return userdb.login(username,sha)


#-------------------------log in fetch.

@app.route('/fetchlogin', methods = [ 'POST'] )
def fetchlogin():
    #print( request.get_json() )
    requestdict = request.get_json()
    #print(type(requestdict)) dict.fine.
    username = requestdict['username']
    sha = requestdict['sha']
    #print(username,sha)

    #token = userdb.user.get(username).get('token')
    token = userdb.login(username,sha)#token='no' if not in.

    if userdb.ismanager(username) or userdb.ismaster(username):
        userlevel = "manager"
    else:
        userlevel = ""
    data = { 'token': token, 'username':username , "userlevel":userlevel}
    return jsonify(data)

@app.route('/fetchnewuser' , methods = [ 'POST'])
def fetchnewuser():
    requestdict = request.get_json()
    username = requestdict['username']
    username = username.replace(' ','_')#for options.value.
    sha = requestdict['sha']
    #print(username,sha)
    data = { 'bodytext' : userdb.newuser(username,sha) }
    return jsonify(data)


#-----------------------button value change
@app.route('/xmlrecomlike' , methods = ['POST'] )
def xmlrecomlike():

    key = request.form['key']
    if key == "recom":
        dbkey = newdb.recom_key
    elif key == "like":
        dbkey = newdb.like_key

    board = request.form['board']
    id = request.form['id']
    token = request.form['token']
    username = userdb.getname(token)
    if username == "noname":
        #return str(len(newdb.db[board][id][dbkey]))
        #익명
        1
        username = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        #return "noname"
    time = datestr()
    # if newdb.press_recom( board, id, time, username) == 1:
    #     return "value1"
    # else:
    #     return "value0"
    newdb.press_recomlike( board, id, time, username, dbkey )
    return str(len(newdb.db[board][id][dbkey]))

@app.route('/xmlview' , methods = ['POST'] )
def xmlview():
    board = request.form['board']
    id = request.form['id']
    dbkey = newdb.view_key

    time = datestr()
    newdb.add_view(board,id, time, 'noname')#fine view ++ button may abuse.

    return str(len(newdb.db[board][id][dbkey]))

@app.route('/xmlcomm' , methods = ['POST'] )
def xmlcomm():

    text = request.form['text']
    board = request.form['board']
    id = request.form['id']
    token = request.form['token']
    username = userdb.getname(token)
    if username == "noname":
        #return "noname"
        1
        #익명

    #print(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))

    time = datestr()
    key = newdb.comm_key
    # if newdb.press_recom( board, id, time, username) == 1:
    #     return "value1"
    # else:
    #     return "value0"
    #newdb.press_recomlike( board, id, time, username, dbkey )
    #return str(len(newdb.db[board][id][dbkey]))

    #print(text,id,board,username,time)# works great.
    userinfo = newdb.setuserinfo(time,username,text, see = newdb.see_default)
    newdb.add(board,id,key,userinfo)
    return "done"

@app.route('/xmldelcomm' , methods = ['POST'] )
def xmldelcomm():
    board = request.form['board']
    id = request.form['id']
    idx = request.form['idx']

    token = request.form['token']
    username = userdb.getname(token)
    if username == "noname":
        return "noname"

    writer = newdb.db[board][id][newdb.comm_key][idx][newdb.user_key]
    #print(username)
    #print(writer)
    if username != writer:
        if userdb.ismanager(username) or userdb.ismaster(username):
            pass
        else:
            return "noname"

    del newdb.db[board][id][newdb.comm_key][idx]
    return "done"

@app.route('/fetchcommload' , methods = [ 'POST'])
def fetchcommload():
    requestdict = request.get_json()
    id = requestdict['id']
    board = requestdict['board']
    token = requestdict['token']

    username = userdb.getname(token)
    #print(username,board,id)
    data = newdb.db[board][id][newdb.comm_key]
    return jsonify(data)


#--------------------------tag
@app.route('/xmltag' , methods = ['POST'] )
def xmltag():

    text = request.form['text']
    board = request.form['board']
    id = request.form['id']
    token = request.form['token']
    username = userdb.getname(token)
    if username == "noname":
        return "noname"

    time = datestr()
    key = newdb.tag_key
    # if newdb.press_recom( board, id, time, username) == 1:
    #     return "value1"
    # else:
    #     return "value0"
    #newdb.press_recomlike( board, id, time, username, dbkey )
    #return str(len(newdb.db[board][id][dbkey]))

    #print(text,id,board,username,time)# works great.

    #dont if already.
    for body in newdb.db[board][id][newdb.tag_key].values():
        if body[newdb.text_key] == text:
            return "done"#simple escape lol

    for t in text.split():
        userinfo = newdb.setuserinfo(time,username,t, see = newdb.see_default)
        newdb.add(board,id,key,userinfo)
    return "done"

@app.route('/xmldeltag' , methods = ['POST'] )
def xmldeltag():
    board = request.form['board']
    id = request.form['id']
    idx = request.form['idx']

    token = request.form['token']
    username = userdb.getname(token)
    if username == "noname":
        return "noname"

    writer = newdb.db[board][id][newdb.tag_key][idx][newdb.user_key]
    if username != writer:
        if userdb.ismanager(username) or userdb.ismaster(username):
            pass
        else:
            return "noname"

    del newdb.db[board][id][newdb.tag_key][idx]
    return "done"

@app.route('/fetchtagload' , methods = [ 'POST'])
def fetchtagload():
    requestdict = request.get_json()
    id = requestdict['id']
    board = requestdict['board']
    token = requestdict['token']

    username = userdb.getname(token)
    #print(username,board,id)
    data = newdb.db[board][id][newdb.tag_key]
    #return newdb.db[board][id][key]
    return jsonify(data)

@app.route('/fetchtaglist' , methods = [ 'POST'])
def fetchtaglist():
    requestdict = request.get_json()
    board = requestdict['board']

    data = newdb.scan_tag(board)
    #data = dict(sorted( data.items() , key= lambda k: len(data[k[0]]) ,reverse= True))
    #dict gone unordered in js.
    return jsonify(data)

#-------------------------sort
@app.route('/getsortlist', methods=[ 'POST'])
def getsortlist():
    if request.method == 'POST':
        board = request.form['board']
        target = request.form['target']
        #newdb.db[board]
        #d=[1,2,3]
        if target == "view":
            d = newdb.lensort(board,newdb.view_key)
        elif target == "recom":
            d = newdb.lensort(board,newdb.recom_key)
        elif target == "comment":
            d = newdb.lensort(board,newdb.comm_key)
        #lensort(board,recom_key)
        #lensort(board,like_key)
        #lensort(board,comm_key)
        return jsonify(d)

@app.route('/likeview', methods=[ 'POST'])
def likeview():
    if request.method == 'POST':
        board = request.form['board']
        token = request.form['token']
        username = userdb.getname(token)
        if username == "noname":
            return "noname"

        user = username
        idList=[]
        for id in newdb.db[board]:
            for i in newdb.db[board][id][newdb.like_key]:
                if newdb.db[board][id][newdb.like_key][i][newdb.user_key] == user:
                    idList.append( id )
        return jsonify(idList)

@app.route('/backupdown', methods=['POST',"GET"])
def backupdown():
    zipfiledir = join('static',"backupzip")
    makedirs(zipfiledir, exist_ok=True)
    for pastz in listdir(zipfiledir):
        pasttime = int(millisec())-int( splitext(pastz)[0] )
        #if pasttime > 3600000:#1hrs.
        #print(pasttime)
        if pasttime > 3600000:#1hrs.
            remove(join(zipfiledir,pastz))
    zipname = '{}.zip'.format(millisec())
    zipdir = join(zipfiledir,zipname)

    with zipfileuni.ZipFile(zipdir, 'w') as zip:
        fname = "data.json"
        zip.write( fname,fname )
        fname = "userdb.json"
        zip.write( fname,fname )

        targetdir1 = join('static','css')
        targetdir2 = join('static','banner')
        targetdir3 = join('static','imgtower')
        targetdirs = [targetdir1,targetdir2,targetdir3]
        for targetdir in targetdirs:
            for folder, subfolders, files in walk(targetdir):
                for file in files:
                    #if file.endswith('.pdf'):
                    zip.write(join(folder, file), join(folder,file) )

    #return zipfiledir
    return send_file( filename_or_fp = zipdir ,as_attachment = True, attachment_filename=datestr()+'.zip')

#-------------------downalod origin dir. img+txt
@app.route('/xmldownzip', methods=['POST'])
def xmldownzip():
    board = request.form['board']
    id = request.form['id']
    imgkey = newdb.originkey
    files = newdb.db[board][id][imgkey]

    zipfiledir = join('static',"tempzip")
    makedirs(zipfiledir, exist_ok=True)

    for pastz in listdir(zipfiledir):
        pasttime = int(millisec())-int( splitext(pastz)[0] )
        if pasttime > 60000:#1min
            remove(join(zipfiledir,pastz))
    zipname = '{}.zip'.format(millisec())
    zipdir = join(zipfiledir,zipname)

    with zipfileuni.ZipFile(zipdir, 'w') as zip:
        for txtfinder in listdir( join('static','imgtower',id) ):
            if splitext(txtfinder)[1]=='.txt':
                zip.write( join('static','imgtower',id,txtfinder),join(id,txtfinder) )
        targetdir = join('static','imgtower',id,'origin')
        for folder, subfolders, files in walk(targetdir):
            for file in files:
                zip.write(join(folder, file), join(id,file) )
    return zipdir
#-------------------downalod origin imgs
@app.route('/xmldownlist', methods=['POST'])
def xmldownlist():
    board = request.form['board']
    id = request.form['id']
    origin = request.form['origin']

    if origin == "true":
        imgkey = newdb.originkey
    else:
        imgkey = newdb.resizedkey

    files = newdb.db[board][id][imgkey]
    s=""
    for f in files:
        s+=f+" "
    return s


@app.route('/multidown', methods=['GET'])
def multidown():
    board = request.args.get('board')
    id = request.args.get('id')
    origin = request.args.get('origin')
    file = request.args.get('file')
    #print(board,id,origin,file)

    if origin == "true":
        imgdir = "origin"
    else:
        imgdir = "resized"

    filepath = join(imgtower_dir,id,imgdir,file)
    filename = newdb.db[board][id][newdb.title_key][:10] + splitext(filepath)[1]
    return send_file( filename_or_fp = filepath ,as_attachment = True, attachment_filename=filename)


@app.route("/getPlotCSV")
def getPlotCSV():
    # with open("outputs/Adjacency.csv") as fp:
    #     csv = fp.read()
    csv = '1,2,3\n4,5,6\n'
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=myplot.csv"})

@app.route('/backup')
def backup():
    newdb.backup()
    return "yeah"

def backupcheck():
    tnow = intsec()
    if tnow - newdb.lastbackuptime>3600:
        newdb.lastbackuptime = tnow
        newdb.backup()

def xmlbackup():
    newdb.lastbackuptime = intsec()
    newdb.backup()

if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0' , port = '12800')
