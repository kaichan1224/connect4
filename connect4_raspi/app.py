from flask import Flask,render_template,request,redirect,url_for,send_from_directory
from game import State
from game import random_action,mcs_action
import json
import os
from copy import deepcopy
from pathlib import Path
import random
import base64
app = Flask(__name__)
app.jinja_env.globals.update(chr=chr)
app.jinja_env.globals.update(int=int)
app.jinja_env.globals.update(base64=base64)
app.jinja_env.globals.update(json=json)

def make_json(data,directory):
    with open(directory,"w") as f:
        json.dump(data,f,indent=4)

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
            values['q'] = random.randint(0,1000)
    return url_for(endpoint, **values)

def monte(state):
    next_action = mcs_action
    #stateのturnがうまく更新できていない問題を解消
    state_copy = deepcopy(state)
    action = next_action(state_copy)
    state = state.next(action)
    return state

def randomchoice(state):
    return state.next(random.randint(0,6))

#タイトル画面
@app.route("/")
def title():
    return render_template("title.html")

@app.route("/game/monte")
def game_alphazero():
    return next("/game/monte",monte)

@app.route("/game/randomchoice")
def game_randomchoice():
    return next("/game/randomchoice",randomchoice)

def next(url,algothim):
    query = request.args.get('query')
    state = State()
    tmp = request.args.get('PlayOrder', '')
    if tmp=="後攻":
        state = algothim(state)
    finish_flag = False
    if query:
        params = json.loads(base64.urlsafe_b64decode(query).decode())
        state = State(params["pieces"],params["enemy_pieces"],params["turn"])
        state = state.next(params["place"])
        if state.is_done():#プレイヤーが終了したら
            finish_flag = True
            return render_template('game.html',url=url,state=State(state.enemy_pieces,state.pieces,state.turn),finish_flag=finish_flag) 
        #AIルーチン
        state = algothim(state)
        if state.is_done():#コンピュータが終了したら
            finish_flag = True
            return render_template('game.html',url=url,state=state,finish_flag=finish_flag) 

    return render_template('game.html',url=url,state=state,finish_flag=finish_flag) 

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)