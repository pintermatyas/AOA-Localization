import ingress_udp_server
import subscription_handler
from threading import Thread

Thread(target=subscription_handler.start_subscription_handler).start()
Thread(target=ingress_udp_server.start_ingress_udp_server).start()