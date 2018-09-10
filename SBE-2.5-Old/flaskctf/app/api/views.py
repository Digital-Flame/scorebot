from flask import request, abort, jsonify
from flask.json import dumps
from . import ctf_api
from .. import db
from ..models import *
from werkzeug.exceptions import BadRequest
from datetime import datetime


@ctf_api.route("/blueteams/", methods=['GET'])
# Test with
# curl -i http://10.150.100.155:5000/scorebot/api/v1.0/blueteams/
def blueteams_getall():
    answer = {}
    entries = [dict(name=row[0], dns=row[1], email=row[2]) \
        for row in db.session.query(Blueteams.name, Blueteams.dns, Blueteams.email).order_by(Blueteams.name)]
    return dumps(entries)

@ctf_api.route("/blueteam/<int:blueteamID>", methods=['GET'])
# Test with
# curl -i http://10.150.100.155:5000/scorebot/api/v1.0/blueteams/2
def blueteams_get(blueteamID):
    answer = {}
    entries = [dict(name=row[0], dns=row[1], email=row[2]) \
        for row in db.session.query(Blueteams.name, Blueteams.dns, Blueteams.email).filter(Blueteams.blueteamID.in_([blueteamID])).order_by(Blueteams.name)]
    return dumps(entries)

@ctf_api.route("/blueteam/", methods=['POST'])
# Test with
# curl -i -H "Content-Type: application/json" -X POST -d '{"name":"EPSILON", "dns":"10.100.105.100", "email":"epsilon@epsilon.net"}' http://localhost:5000/scorebot/api/v1.0/blueteams/
def blueteams_put():
    if not request.json or not 'name' in request.json:
        abort(400)
    name = request.json['name']
    dns = request.json['dns']
    email = request.json['email']
    bt = Blueteams(name=name, dns=dns, email=email)
    db.session.add(bt)
    db.session.commit()
    return jsonify({}), 201

@ctf_api.route("/games/", methods=['GET'])
# Test with
# curl -i http://10.150.100.155:5000/scorebot/api/v1.0/games/
def games_getall():
    entries = [dict(name=row[0], date=row[1]) \
               for row in db.session.query(Games.name, Games.date).order_by(Games.date)]
    return dumps(entries)

@ctf_api.route("/game/<int:gameID>", methods=['GET'])
# Test with
# curl -i http://10.150.100.155:5000/scorebot/api/v1.0/game/1
def games_get(gameID):
    entries = [dict(name=row[0], date=row[1]) \
               for row in db.session.query(Games.name, Games.date).filter(Games.gameID.in_([gameID])).order_by(Games.date)]
    return dumps(entries)

@ctf_api.route("/game/", methods=['POST'])
# Test with
# curl -i -H "Content-Type: application/json" -X POST -d '{"name":"Game1", "date":"05/01/2015"}' http://localhost:5000/scorebot/api/v1.0/game/
def game_put():
    if not request.json or (not 'name' in request.json and not 'date' in request.json) :
        abort(400)
    name = request.json['name']
    date = request.json['date']
    game = Games(name=name, date=date)
    db.session.add(game)
    db.session.commit()
    return jsonify({}), 201

@ctf_api.route("/hosts/", methods=['GET'])
# Test with
# curl -i http://10.150.100.155:5000/scorebot/api/v1.0/game/1
def hosts_get():
    entries = [dict(name=row[0], date=row[1]) \
               for row in db.session.query(Hosts.blueteamID, Hosts.gameID, Hosts.hostname, Hosts.value).order_by(Hosts.hostname)]
    return dumps(entries)

@ctf_api.route("/host/<int:hostID>", methods=['GET'])
# Test with
# curl -i http://10.150.100.155:5000/scorebot/api/v1.0/game/1
def host_get(hostID):
    entries = [dict(name=row[0], date=row[1]) \
               for row in db.session.query(Hosts.blueteamID, Hosts.gameID, Hosts.hostname, Hosts.value).filter(Hosts.hostID.in_([hostID])).order_by(Hosts.hostname)]
    return dumps(entries)

@ctf_api.route("/host/", methods=['POST'])
# Test with
# curl -i -H "Content-Type: application/json" -X POST -d '{"blueteam":"EPSILON", "game":"Game1", "hostname":"domain.epsilon.net", "value":"100"}' http://localhost:5000/scorebot/api/v1.0/host/
def host_put():
    if not request.json:
        raise BadRequest("No data sent!")
    if 'blueteam' in request.json:
        name = request.json['blueteam']
    else:
        raise BadRequest("Blueteam name not sent!")
    bt = Blueteams.query.filter_by(name=name).first()
    if bt:
        btID = bt.blueteamID
    else:
        raise BadRequest("Blueteam %s not found!" % name)
    if 'game' in request.json:
        name = request.json['game']
    else:
        raise BadRequest("Game name not sent!")
    game = Games.query.filter_by(name=name).first()
    if game:
        gameID = game.gameID
    else:
        raise BadRequest("Game %s not found!" % name)
    print btID, gameID
    if 'hostname' in request.json:
        hostname = request.json['hostname']
    else:
        raise BadRequest("Hostname not sent!")
    if 'value' in request.json:
        value = request.json['value']
    else:
        raise BadRequest("Value not sent!")
    host = Hosts(blueteamID=btID, gameID=gameID, hostname=hostname, value=value)
    db.session.add(host)
    db.session.commit()
    return jsonify({}), 201


@ctf_api.route("/hoststatus/<int:host_id>", methods=['POST'])
def hoststatus_set(host_id):
    """
    curl -i -H "Content-Type: application/json" -X POST -d '{"status":"UP"}' http://localhost:5000/scorebot/api/v1.0/hoststatus/<host_id>
    """
    if not request.json:
        raise BadRequest("No data sent!")
    host = Hosts.query.get(host_id)
    if not host:
        raise BadRequest("Host with id of %d not found" % host_id)
    if 'status' in request.json:
        status = request.json['status']
    else:
        raise BadRequest("Status not sent!")
    date = datetime.utcnow()
    try:
        HostStatus.query.filter_by(hostID=host_id).update(dict(status=status,
                                                               datetime=date))
    except:
        host_status = HostStatus(status=status, hostID=host_id, datetime=date)
        db.session.add(host_status)
    db.session.commit()
    return jsonify({}), 201


@ctf_api.route("/player/", methods=['POST'])
def player_put():
    """
    curl -i -H "Content-Type: application/json" -X POST -d '{"username":"gi0cann", "firstname":"Gionne", "lastname":"Cannister", "score":"0", "password":"abcd1234"}' http://localhost:5000/scorebot/api/v1.0/player/
    """
    if not request.json:
        raise BadRequest("No data sent!")
    if 'username' in request.json:
        username = request.json['username']
    else:
        raise BadRequest("No username data sent!")
    if 'firstname' in request.json:
        firstname = request.json['firstname']
    else:
        raise BadRequest("No firstname data sent!")
    if 'lastname' in request.json:
        lastname = request.json['lastname']
    else:
        raise BadRequest("No lastname data sent!")
    if 'score' in request.json:
        score = request.json['score']
    else:
        raise BadRequest("No score data sent!")
    if 'password' in request.json:
        password = request.json['password']
    else:
        raise BadRequest("No password data sent!")
    player = Players(username=username, firstName=firstname, lastName=lastname,
                     score=score, password=password)
    db.session.add(player)
    db.session.commit()
    return jsonify({}), 201


@ctf_api.route("/player/<int:player_id>", methods=['PUT'])
def player_update(player_id):
    """
    Updates player information
    curl -i -H "Content-Type: application/json" -X PUT -d '{"username":"gi0cann", "firstname":"Gionne", "lastname":"Cannister", "score":"0", "password":"abcd1234"}' http://localhost:5000/scorebot/api/v1.0/player/<player_id>
    """
    values = dict()
    if not request.json:
        raise BadRequest("No data sent!")
    if 'username' in request.json:
        values['username'] = request.json['username']
    if 'firstname' in request.json:
        values['firstName'] = request.json['firstname']
    if 'lastname' in request.json:
        values['lastName'] = request.json['lastname']
    if 'score' in request.json:
        values['score'] = request.json['score']
    if 'password' in request.json:
        values['password'] = request.json['password']
    Players.query.filter_by(playerID=player_id).update(values)
    db.session.commit()
    return jsonify({}), 201


@ctf_api.route("/service/", methods=['POST'])
def service_put():
    """
curl -i -H "Content-Type: application/json" -X POST -d '{"protocol":"tcp", "hostname":"domain.epsilon.net", "name":"dns", "value":"100", "port":"53"}' http://localhost:5000/scorebot/api/v1.0/service/
    """
    if not request.json:
        raise BadRequest("No data sent!")
    if 'hostname' in request.json:
        hostname = request.json['hostname']
    else:
        raise BadRequest("Hostname not sent!")
    host = Hosts.query.filter_by(hostname=hostname).first()
    if host:
        hostID = host.hostID
    else:
        raise BadRequest("Host %s not found!" % name)
    if 'protocol' in request.json:
        protocol = request.json['protocol']
    else:
        raise BadRequest("Protocol not sent!")
    if 'value' in request.json:
        value = request.json['value']
    else:
        raise BadRequest("Value not sent!")
    if 'name' in request.json:
        name = request.json['name']
    else:
        raise BadRequest("Name not sent!")
    if 'port' in request.json:
        port = request.json['port']
    else:
        raise BadRequest("Port not sent!")
    service = Services(protocol=protocol, hostID=hostID, name=name, value=value,
                       port=port)
    db.session.add(service)
    db.session.commit()
    return jsonify({}), 201


@ctf_api.route("/servicestatus/<int:service_id>", methods=['POST'])
def servicestatus_set(service_id):
    """
curl -i -H "Content-Type: application/json" -X POST -d '{"status":"UP"}' http://localhost:5000/scorebot/api/v1.0/servicestatus/<service_id>
    """
    if not request.json:
        raise BadRequest("No data sent!")
    service = Services.query.get(service_id)
    if not service:
        raise BadRequest("Service with id of %d not found" % service_id)
    if 'status' in request.json:
        status = request.json['status']
    else:
        raise BadRequest("Status not sent!")
    date = datetime.utcnow()
    try:
        ServiceStatus.query.filter_by(serviceID=service_id).update(
            dict(status=status, datetime=date))
    except:
        service_status = ServiceStatus(status=status, serviceID=service_id,
                                       datetime=date)
        db.session.add(service_status)
    db.session.commit()
    return jsonify({}), 201


@ctf_api.route("/flagstolen/<int:flag_id>", methods=['POST'])
def flagstolen_set(flag_id):
    """
curl -i -H "Content-Type: application/json" -X POST -d '{"player_id":"1", "activity":"dns"}' http://localhost:5000/scorebot/api/v1.0/flagstolen/<flag_id>
    """
    if not request.json:
        raise BadRequest("No data sent!")
    flag = Flags.query.get(flag_id)
    if not flag:
        raise BadRequest("Flag with id of %d not found" % flag_id)
    if 'player_id' in request.json:
        player_id = request.json['player_id']
    player = Players.query.get(flag_id)
    if not player:
        raise BadRequest("Player with id of %d not found" % flag_id)
    if 'activity' in request.json:
        activity = request.json['activity']
    else:
        raise BadRequest("Activity not sent!")
    date = datetime.utcnow()
    flagstolen = FlagsStolen(playerID=player_id, flagID=flag_id,
                             activity=activity, datetime=date)
    db.session.add(flagstolen)
    db.session.commit()
    return jsonify({}), 201


@ctf_api.route("/flagsfound/<int:flag_id>", methods=['POST'])
def flagfound_set(flag_id):
    """
curl -i -H "Content-Type: application/json" -X POST -d '{"player_id":"1", "activity":"dns"}' http://localhost:5000/scorebot/api/v1.0/flagsfound/<flag_id>
    """
    if not request.json:
        raise BadRequest("No data sent!")
    flag = Flags.query.get(flag_id)
    if not flag:
        raise BadRequest("Flag with id of %d not found" % flag_id)
    if 'player_id' in request.json:
        player_id = request.json['player_id']
    player = Players.query.get(flag_id)
    if not player:
        raise BadRequest("Player with id of %d not found" % flag_id)
    if 'activity' in request.json:
        activity = request.json['activity']
    else:
        raise BadRequest("Activity not sent!")
    date = datetime.utcnow()
    flagfound = FlagsFound(playerID=player_id, flagID=flag_id,
                           activity=activity, datetime=date)
    db.session.add(flagfound)
    db.session.commit()
    return jsonify({}), 201


@ctf_api.route("/flag/", methods=['POST'])
def flag_put():
    """
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"EPdns", "blueteam":"EPSILON", "game":"Game1", "answer":"Nice!!", "value":"abcd1234", "points":"100"}' http://localhost:5000/scorebot/api/v1.0/flag/
    """
    if not request.json:
        raise BadRequest("No data sent!")
    if 'blueteam' in request.json:
        name = request.json['blueteam']
    else:
        raise BadRequest("Blueteam name not sent!")
    bt = Blueteams.query.filter_by(name=name).first()
    if bt:
        btID = bt.blueteamID
    else:
        raise BadRequest("Blueteam %s not found!" % name)
    if 'game' in request.json:
        name = request.json['game']
    else:
        raise BadRequest("Game name not sent!")
    game = Games.query.filter_by(name=name).first()
    if game:
        gameID = game.gameID
    else:
        raise BadRequest("Game %s not found!" % name)
    print btID, gameID
    if 'name' in request.json:
        flag_name = request.json['name']
    else:
        raise BadRequest("Name not sent!")
    if 'value' in request.json:
        value = request.json['value']
    else:
        raise BadRequest("Value not sent!")
    if 'points' in request.json:
        points = request.json['points']
    else:
        raise BadRequest("Points not sent!")
    if 'answer' in request.json:
        answer = request.json['answer']
    else:
        raise BadRequest("Answer not sent!")
    flag = Flags(blueteamID=btID, gameID=gameID, name=flag_name, value=value,
                 answer=answer, points=points)
    db.session.add(flag)
    db.session.commit()
    return jsonify({}), 201
