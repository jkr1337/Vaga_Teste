from flask import Flask, request, jsonify

app = Flask(__name__)

balances = {"1234":223}

def deposit(destination, amount):
    global balances
    retorno = {}
    retorno_body = {}
    http_return = 400

    balances[destination] = balances.get(destination, 0) + amount

    retorno_body['id'] = destination
    retorno_body['balance'] = balances[destination]
    retorno['destination'] = retorno_body
    http_return = 201

    return retorno, http_return

def withdraw(origin, amount):
    global balances
    retorno = {}
    retorno_body = {}
    http_return = 400

    if origin not in balances:
        retorno['error'] = 'user not found'
        http_return = 400
    elif balances[origin] < amount:
        retorno['error'] = 'insufficient balance'
        http_return = 400
    else:
        balances[origin] = balances[origin] - amount
        retorno_body['id'] = origin
        retorno_body['balance'] = balances[origin]  
        retorno['origin'] = retorno_body              
        http_return = 201

    return retorno, http_return

@app.route('/reset', methods=['POST'])
def reset():
    global balances
    balances = {}

    return jsonify({'reset':'OK'}), 200

@app.route('/balance', methods=['GET'])
def get_balance():
    account_id = request.args.get("account_id")

    if account_id not in balances:
        return jsonify(0), 404
    
    return jsonify({'account_id': account_id, 'balance': balances[account_id]})

@app.route('/event', methods=['POST'])
def handle_event():
    retorno = {}
    retorno_body = {}
    http_return = 400
    retorno_withdraw = {}
    retorno_deposit = {}
    data = request.json

    if 'type' in data:
        type = data['type']

        if type == 'deposit':
            if 'destination' in data:
                destination = data['destination']
            if 'amount' in data:
                amount = data['amount']

            retorno, http_return = deposit(destination, amount)

        if type == 'withdraw':
            if 'origin' in data:
                origin = data['origin']
            if 'amount' in data:
                amount = data['amount']

            retorno, http_return = withdraw(origin, amount)

        if type == 'transfer':
            if 'origin' in data:
                origin = data['origin']
            if 'destination' in data:
                destination = data['destination']
            if 'amount' in data:
                amount = data['amount']

            retorno_withdraw, http_return = withdraw(origin, amount)

            if http_return != 201:
                retorno['error'] = 'cant transfer'
            else:
                retorno_deposit, http_return = deposit(destination, amount)

            for key, value in retorno_withdraw.items():
                retorno[key] = value
            for key, value in retorno_deposit.items():
                retorno[key] = value

    return jsonify(retorno), http_return


if __name__ == '__main__':
    app.run(port=8080)