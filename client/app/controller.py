from . import cli as ui
import paho.mqtt.client as mqtt
import time
import json

EXIT_BTN = ""
TERM_READING_QUERY = "Terminals reading"
TERM_CONNECTING_QUERY = "Terminal connected"
TERM_DISCONNECTING_QUERY = "Terminal disconnected"
TERM_SELECTED_QUERY = "Terminal selected"
CARD_READING_QUERY = "Card read"
CONFIG_PATH = "config/conf.json"


class ClientController:
    def __init__(self):
        self.__client_active = True
        self.__not_logged = True
        self.__client = mqtt.Client("CLIENT CONTROLLER")
        self.__term_guid = None
        self.__term_list = None
        self.config = ClientController.read(CONFIG_PATH)

    def run(self):
        self.setup()
        self.read_terminal()
        while self.__client_active:
            ui.show_data(ui.SCAN_CARD_PROMPT)
            card_guid = self.scan_card()
            self.__client_active = not card_guid == EXIT_BTN
            if card_guid != EXIT_BTN:
                self.register_card_usage(card_guid)
        self.disconnect_from_broker()

    def setup(self):
        self.connect_to_broker()
        self.query_available_terminals()
        self.__client.loop_start()

    def connect_to_broker(self):
        """
        Nawiązuję połączenie z serwerem używając protokół MQTT,
        podpisuje `terminal` topic i wysyła powiadomienia do serwera o połączeniach
        """
        self.__client.tls_set(self.config["cert_path"])
        self.__client.username_pw_set(
            username=self.config["username"], password=self.config["password"])
        self.__client.connect(self.config["broker"], self.config["port"])
        self.__client.subscribe(self.config["term_topic"])
        self.__client.on_message = self.process_message
        self.__client.publish(
            self.config["server_topic"], TERM_CONNECTING_QUERY)

    def process_message(self, client, userdata, message):
        # Getting terminal
        if self.__not_logged:
            self.__term_list = (
                str(message.payload.decode("utf-8"))).split(".")

    def disconnect_from_broker(self):
        """
        Rozłącza terminal klienta z serwera
        """
        self.__client.publish(
            self.config["server_topic"], TERM_DISCONNECTING_QUERY + "." + self.__term_guid)
        self.__client.disconnect()

    def query_available_terminals(self):
        self.__client.publish(self.config["server_topic"], TERM_READING_QUERY)

    def read_terminal(self):
        self.wait_for_server_response()
        self.check_any_terminal_registered()
        ui.show_data(ui.TERMINALS_READED)
        self.__term_guid = self.choose_terminal()
        query = TERM_SELECTED_QUERY + "." + "ID of connected terminal:." + self.__term_guid
        self.__client.publish(self.config["server_topic"], query)

    def check_any_terminal_registered(self):
        if len(self.__term_list) == 0:
            ui.show_data(ui.NOT_FOUND_TERMINAL)
            ui.read_data(ui.INPUT_WAITING)
            exit(0)

    def choose_terminal(self):
        ui.show_data(ui.TERMINALS_MENU)
        ui.show_data(self.__term_list)

        term_guid = ui.read_data(ui.TERMINAL_INPUT)
        while term_guid not in self.__term_list:
            ui.show_data(term_guid + ": " + ui.INCORRECT_TERMINAL +
                         "\n" + ui.SEPARATOR + "\n" + ui.TERMINALS_MENU)
            ui.show_data(self.__term_list)
            term_guid = ui.read_data(ui.TERMINAL_INPUT)
        return term_guid

    def register_card_usage(self, card_guid):
        ui.show_data(ui.CARD_SCANNED)
        self.query_card_usage(card_guid, self.__term_guid)

    def query_card_usage(self, card_guid, terminal_guid):
        self.__client.publish(
            self.config["server_topic"], CARD_READING_QUERY + "." + card_guid + "." + terminal_guid)

    def wait_for_server_response(self):
        ui.show_data(ui.WAITING_FOR_SERVER)
        while self.__term_list is None:
            time.sleep(2)
            self.query_available_terminals()

    def scan_card(self):
        prompt = "Temporary mocked - put card id from keyboard or nothing to exit: "
        user_input = ui.read_data(prompt)
        while not user_input.isdigit() and not user_input == EXIT_BTN:
            ui.show_data(ui.WRONG_CARD_GUID)
            user_input = ui.read_data(prompt)
        return user_input

    @staticmethod
    def read(path):
        with open(path, "r") as f:
            content = f.read()
        return json.loads(content)
