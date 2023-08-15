from kombu import Producer, Connection, Consumer, Queue, Exchange


class MQUtils:
    '''
    utility class that handles all logic related to connecting to
    rabbitMQ, publishing and consuming messages from a queue
    '''

    def __init__(self):
        import logging
        self.connection:Connection = Connection("amqp://user:password@broker:5672//").connect()#connect to amqp server here
        self.channel = self.connection.channel()
        logging.info(f'connection instance: {self.connection}')
        # create direct exchange
        self.direct_exchange = self.default_direct_exchange()
        logging.info("direct exchange created users")
        # create a default group exchange
        # self.group_exchange = self.default_group_exchange()
        logging.info("group exchange created for users")


    def get_direct_consumer(self)->Consumer:
        with self.channel as chann:
            consumer:Consumer = chann.Consumer(queues=[])
            consumer.declare()
            return consumer
    

    def get_group_consumer(self)->Consumer:
        consumer:Consumer = self.channel.Consumer(queues=[], call_backs=[])
        consumer.declare()
        return consumer
    

    def get_default_publisher(self)->Producer:
        with self.channel as channel:
            publisher:Producer = channel.Producer()
            publisher.declare()
            return publisher
    
    def default_direct_exchange(self)->Exchange:
        '''
        a default exchange to be used by all
        users for one on one interaction
        '''
        with self.connection as conn:
            exchange:Exchange = Exchange(name="users_channel", type="direct", channel=self.channel)
            exchange.declare()
            return exchange
    
    def default_group_exchange(self)->Exchange:
        '''
        a topic exchange reserved for anyone
        who wants to create a group
        '''
        group_exchange:Exchange = Exchange(name="Group Topics", type="topic", channel=self.channel)
        group_exchange.declare()
        return group_exchange

    def create_user_direct_queue(self, name:str="No User")->Queue:
        '''
        creates a queue when needed, especially when new user connects to the backend
        '''
        user_queue:Queue = Queue(name=name, routing_key=name, exchange=self.direct_exchange, channel=self.channel)
        user_queue.declare()
        # let the direct consumer start consuming from this queue
        self.get_direct_consumer().add_queue(user_queue).consume()
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
    
    def default_setup(self):
        '''
        initializes connections and other things necessary, on startup
        '''
        direct_consumer = self.get_direct_consumer()
        group_consumer = MQUtils.get_group_consumer()
        direct_exchange = MQUtils.default_direct_exchange()
        group_exchange = MQUtils.default_group_exchange()
        # direct_queue = MQUtils.create_user_direct_queue()
        default_publisher = MQUtils.get_default_publisher()
        messaging_infos = {
            "connection": self.connection,
            "direct_consumer": direct_consumer,
            "group_consumer": group_consumer,
            "direct_exchange": direct_exchange,
            "group_exchange": group_exchange,
            # "direct_queue": direct_queue,
            "default_publisher": default_publisher
        }
        return messaging_infos