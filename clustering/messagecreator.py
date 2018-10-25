import uuid


def rpc_func_state(state):
    return {'status': 'state', 'state': state}


def rpc_func_result(status, msgs_bulk):
    return {'status': status, 'bulk': msgs_bulk}


def rpc_wrapped_result(result, node_id, flow_id, log_msg_id):
    return {
        'node_id': node_id,
        'flow_id': flow_id,
        'result': result,
        'msg_id': log_msg_id
    }


def rpc_func_request(msgs_bulk, func, node_properties):
    bulk_id = str(uuid.uuid4())
    return {
        'func': func,
        'msgs_bulk': msgs_bulk,
        'node_config': node_properties,
        'bulk_id': bulk_id
    }


def rpc_recipe_request(msgs_bulk, recipe_id, node_properties, node_id, flow_id):
    bulk_id = str(uuid.uuid4())
    return {
        'node_id': node_id,
        'flow_id': flow_id,
        'recipe_id': recipe_id,
        'msgs_bulk': msgs_bulk,
        'node_config': node_properties,
        'bulk_id': bulk_id
    }
