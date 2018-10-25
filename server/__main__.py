import json

from multiprocessing import Queue
from flask import Flask, request, abort, send_from_directory
from fbp.fbppool import App


# dir_path = "C:\\Users\\alpha\\Documents\\Flash - new\\server\\build"
# dir_path = "build"


app = Flask('__main__', static_folder='static')


@app.route('/')
def serve():
    return send_from_directory('static', 'index.html')


@app.route('/flows', methods=['GET'])
def get_flow_list():
    conf = __load_config('../fbp.config')
    flows = conf['flows']
    flow_list = list(map(lambda f: {'flow_id': f['flow_id'], 'name': f['name']}, flows))
    print(json.dumps(flow_list))
    return json.dumps(flow_list)


@app.route('/flows/<flow_id>', methods=['GET'])
def get_flow(flow_id):
    conf = __load_config('../fbp.config')
    flows = conf['flows']
    flow = next(f for f in flows if f['flow_id'] == flow_id)

    print(flow['nodes'])

    return json.dumps(flow)


@app.route('/flows/<flow_id>', methods=['PUT'])
def add_node_to_flow(flow_id):
    if not request.json:
        abort(400)
    node_type = request.json

    print(node_type)

#    fbp_app = App('../fbp.config')
    node = fbp_app.generate_node(flow_id, node_type)
    #    validate_node(node)

    bla = node.toJSON()
    return json.dumps(bla)


@app.route('/nodes', methods=['GET'])
def get_default_nodes():
    conf = __load_config('../fbp.config')
    nodes = conf['default_nodes']
    print(nodes)
    return json.dumps(nodes)


@app.route('/status/<flow_id>', methods=['GET'])
def get_status(flow_id):
    with open('C:\\Docs\\flash\\flashstatus\\%s-status.json' % flow_id, 'r') as status_file:
        status = status_file.read()
        return json.dumps(status)


@app.route('/content/<node_id>', methods=['GET'])
def show_queue(node_id):
 #   if not request.json:
 #       abort(400)
#    request_contents_msg = request.json

  #  print(request_contents_msg)

    contents = fbp_app.get_node_content(node_id, 0)
    data = json.dumps(contents)
    return data


def __load_config(config_path):
    with open(config_path, 'r') as config_file:
        config = config_file.read()
        return json.loads(config)


def update_flow(flow_id, node):
    conf = __load_config('../fbp.config')
    flows = conf['flows']
    flow = next(f for f in flows if f['flow_id'] == flow_id)

    if flow is None:
        return False

    print(flow)
    index = (i for i, e in enumerate(flow['nodes']) if e['node_id'] == node['node_id'])

    if index is None:
        flow['nodes'].append(node)
    else:
        flow['nodes'][index] = node

    print(flow)
    return True


if __name__ == '__main__':
    tasks_q = Queue()
    results_q = Queue()
    fbp_app = App('../fbp.config', tasks_q, results_q)
    # fbp_app.start_flows()
    app.run(host='0.0.0.0')
    print(fbp_app)
