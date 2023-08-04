from kombu import Producer, Connection, Consumer, Queue, Exchange


class MQUtils:
    '''
    utility class that handles all logic related to connecting to
    rabbitMQ, publishing and consuming messages from a queue
    '''
    @staticmethod
    def _get_connection():
        connection = Connection()#connect to amqp server here
        return connection

    @staticmethod
    def get_consumer():
        consumer = MQUtils._get_connection().Consumer(queues=[])
        return consumer
    
    @staticmethod
    def get_publisher():
        publisher = MQUtils._get_connection().Producer()
    
    @staticmethod
    def default_exchange():
        '''
        a default exchange to be used by all
        users for one on one interaction
        '''
        exchange = Exchange(name="users_channel", type="direct", channel=MQUtils._get_connection().channel())
        return exchange
    
    @staticmethod
    def create_group_exchange(group_name:str):
        '''
        a topic exchange reserved for anyone
        who wants to create a group
        '''
        group_exchange = Exchange(name=group_name, type="topic", channel=MQUtils._get_connection().channel())
        group_exchange.declare()
        # save the exchange name to the db for refrence
        return group_exchange

    @staticmethod
    def create_user_queue(name, existing_queue=None, for_a_group=False, group_name=None):
        '''
        creates a queue when needed, especially when new user connects to the backend
        '''
        if not (existing_queue and for_a_group and group_name):
            default_connection = MQUtils._get_connection()
            user_queue = Queue(name=name, routing_key=name, exchange=MQUtils.default_exchange())
            user_queue.declare()
            return user_queue
        # else add the user existing user_queue to the topic exchange they want to join
        
    