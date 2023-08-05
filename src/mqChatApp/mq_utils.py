from kombu import Producer, Connection, Consumer, Queue, Exchange


class MQUtils:
    '''
    utility class that handles all logic related to connecting to
    rabbitMQ, publishing and consuming messages from a queue
    '''
    @staticmethod
    def _get_connection():
        connection = Connection()#connect to amqp server here
        connection.drain_events()
        return connection

    @staticmethod
    def get_direct_consumer()->Consumer:
        consumer = MQUtils._get_connection().Consumer(queues=[], channel=MQUtils._get_connection().channel(), call_backs=[MQUtils.direct_consumer_callback()])
        consumer.declare()
        return consumer
    
    @staticmethod
    def get_group_consumer()->Consumer:
        consumer = MQUtils._get_connection().Consumer(queues=[], channel=MQUtils._get_connection().channel(), call_backs=[MQUtils.group_consumer_callback()])
        consumer.declare()
        return consumer
    
    @staticmethod
    def get_default_publisher()->Producer:
        publisher = MQUtils._get_connection().Producer()
        publisher.declare()
        return publisher
    
    @staticmethod
    def default_direct_exchange():
        '''
        a default exchange to be used by all
        users for one on one interaction
        '''
        exchange = Exchange(name="users_channel", type="direct", channel=MQUtils._get_connection().channel())
        exchange.declare()
        return exchange
    
    @staticmethod
    def default_group_exchange():
        '''
        a topic exchange reserved for anyone
        who wants to create a group
        '''
        group_exchange = Exchange(name="Group Topics", type="topic", channel=MQUtils._get_connection().channel())
        group_exchange.declare()
        return group_exchange

    @staticmethod
    def create_user_direct_queue(name="No User"):
        '''
        creates a queue when needed, especially when new user connects to the backend
        '''
        default_connection = MQUtils._get_connection()
        user_queue = Queue(name=name, routing_key=name, exchange=MQUtils.default_direct_exchange(), channel=default_connection.channel())
        user_queue.declare()
        # let the direct consumer start consuming from this queue
        MQUtils.get_direct_consumer().add_queue(user_queue).consume()
        return user_queue
        # else add the user existing user_queue to the topic exchange they want to join
    
    @staticmethod
    def create_user_group_queue(username:str, group_name:str, new_group:bool=False)->tuple:
        '''
        the queue created for the user when creating or joining a group
        '''
        joined_group = False
        if not new_group:
            # user wants to join an existing group
            joined_group = True
            # retrieve group info from the db, using group_name for processing
            # when publishing to this exchange, the routing_key must be of pattern: *.{group_name}
            user_group_queue = Queue(name=f"{username}.{group_name}", routing_key=f"{username}.{group_name}", exchange=MQUtils.default_group_exchange(), channel=MQUtils._get_connection().channel())
            MQUtils.get_group_consumer().add_queue(user_group_queue).consume()
            return user_group_queue, joined_group
        # user wants to create a new group
        user_group_queue = Queue(name=f"{username}.{group_name}", routing_key=f"{username}.{group_name}", exchange=MQUtils.default_group_exchange(), channel=MQUtils._get_connection().channel())
        MQUtils.get_group_consumer().add_queue(user_group_queue).consume()
        return user_group_queue, joined_group
    
    @staticmethod
    def default_setup():
        '''
        initializes connections and other things necessary, on startup
        '''
        connection = MQUtils._get_connection()
        direct_consumer = MQUtils.get_direct_consumer()
        group_consumer = MQUtils.get_group_consumer()
        direct_exchange = MQUtils.default_direct_exchange()
        group_exchange = MQUtils.default_group_exchange()
        # direct_queue = MQUtils.create_user_direct_queue()
        default_publisher = MQUtils.get_default_publisher()
        messaging_infos = {
            "connection": connection,
            "direct_consumer": direct_consumer,
            "group_consumer": group_consumer,
            "direct_exchange": direct_exchange,
            "group_exchange": group_exchange,
            # "direct_queue": direct_queue,
            "default_publisher": default_publisher
        }
        return messaging_infos