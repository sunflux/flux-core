import multiprocessing

#from fbp.port import Port

# relation types
STATUS_SUCCESS = "success"
STATUS_FAIL = "fail"
STATUS_INIT = "init"
STATUS_RUNNING = "running"


class Relation(object):

    def __init__(self, relation_id, name, relation_type, events, bulks_capacity, src_node_id, dst_node_id):
        self.id = relation_id
        self.name = name
        #self.src_node = src_node
        #self.dst_node = dst_node
        self.src_node_id = src_node_id
        self.dst_node_id = dst_node_id
        self.type = relation_type
        self.events = events
        self.bulk_capacity = bulks_capacity

        self.dst_node = None
        self.q = multiprocessing.Queue()

    def deque(self):
        msgs_bulk = self.q.get()
        self.dst_node.enqueue(msgs_bulk)
        print('Transferred bulk to designated node')

    def enqueue(self, msgs_bulk):
        #if self.q.qsize() == self.bulk_capacity:
        if self.dst_node.q.qsize() == self.bulk_capacity:
            # TODO: replace with a block/callback
            return
        self.q.put(msgs_bulk)
        print("Added a bulk to relation %s" % self.id)
        self.deque()


class RelationManager(object):

    def __init__(self, possible_relations):
        self.active_relations = {}
        self.possible_relations = possible_relations

    def add_relation(self, relation):
        if relation.type in self.active_relations:
            self.active_relations[relation.type].append(relation)
        else:
            self.active_relations[relation] = [relation]

    # event as: 'Success', 'Failure' etc
    def send_msg_on_event(self, event, msg):
        event_relations = filter(lambda relation: relation.type == event, self.active_relations)

        for rel in event_relations:
            rel.enqueue(msg)

