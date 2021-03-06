from datetime import datetime
from app.logic.server import Server, DataInputError
import app.ui.cli as ui
import paho.mqtt.client as mqtt

TERM_READING_QUERY = "Terminals reading"
TERM_CONNECTING_QUERY = "Terminal connected"
TERM_DISCONNECTING_QUERY = "Terminal disconnected"
TERM_SELECTED_QUERY = "Terminal selected"
CARD_READING_QUERY = "Card read"


class ServerController:
    def __init__(self):
        self.server = Server()
        self.__client = mqtt.Client("SERVER_CONTROLLER")
        self.__server_active = True
        self.tracking_activity = False

    def run(self):
        self.connect_to_broker()
        while self.__server_active:
            ui.ServerMenu.show()
            menu_option = ServerController.get_menu_option()
            self.open_menu_option(menu_option)
        self.disconnect_from_broker()

    def connect_to_broker(self):
        config = self.server.get_configs()
        self.__client.tls_set(config["cert_path"])
        self.__client.username_pw_set(username=config["username"], password=config["password"])
        self.__client.connect(config["broker"], config["port"])
        self.__client.on_message = self.process_message
        self.__client.subscribe(config["server_topic"])
        self.__client.loop_start()

    def process_message(self, client, userdata, message):
        decoded = (str(message.payload.decode("utf-8"))).split(".")
        if decoded[0] == TERM_READING_QUERY:
            self.term_reading_query()
        elif decoded[0] == TERM_CONNECTING_QUERY:
            self.term_connecting_query(decoded[0])
        elif decoded[0] == TERM_DISCONNECTING_QUERY:
            self.term_disconnection_query(decoded[0], decoded[1])
        elif decoded[0] == TERM_SELECTED_QUERY:
            self.term_selected_query(decoded[1], decoded[2])
        elif decoded[0] == CARD_READING_QUERY:
            self.card_reading_query(decoded[1], decoded[2])
        else:
            ui.show_msg("Unknown query")

    def term_reading_query(self):
        self.__client.publish(self.server.get_configs()["term_topic"], self.available_term_query())

    def term_connecting_query(self, msg):
        if self.tracking_activity:
            ui.show_msg(msg)
            ui.show_msg(ui.SEPARATOR)

    def term_disconnection_query(self, msg, term_guid):
        if self.tracking_activity:
            ui.show_msg(msg)
            ui.show_msg(ui.SEPARATOR)
        self.server.set_terminal_engage(term_guid, False)

    def term_selected_query(self, msg, term_guid):
        self.server.set_terminal_engage(term_guid, True)
        if self.tracking_activity:
            ui.show_msg(msg + term_guid)
        ui.show_msg(ui.SEPARATOR)

    def card_reading_query(self, card_guid, term_guid):
        card_owner = self.server.register_card_usage(card_guid, term_guid)
        if self.tracking_activity:
            ServerController.show_card_usage_msg(card_guid, card_owner, term_guid)

    @staticmethod
    def show_card_usage_msg(card_guid, card_owner, terminal_id):
        ui.show_msg(ui.CARD_USAGE_REGISTERED)
        ui.show_msg("Card GUID= " + card_guid)
        if card_owner is None:
            ui.show_msg(ui.UNKNOWN_CARD_OWNER)
        else:
            owner_guid = card_owner.worker_guid
            owner_fullname = card_owner.name + " " + card_owner.surname
            ui.show_msg(ui.CARD_OWNER_IS_KNOWN + owner_guid + ", " + owner_fullname)
        ui.show_msg("Terminal ID= " + terminal_id)
        ui.show_msg(ui.SEPARATOR)

    def available_term_query(self):
        term_msg = ""
        for k in self.server.get_terminals().keys():
            if not self.server.terminal_is_engaged(k):
                term_msg += (k + ".")
        if term_msg == "":
            return term_msg
        return term_msg[:-1]  # skipping last dot

    def disconnect_from_broker(self):
        self.__client.loop_stop()
        self.__client.disconnect()

    @staticmethod
    def get_menu_option():
        user_input = input(ui.CHOOSE_MENU_OPTION)
        while not user_input.isdigit():
            ServerController.incorrect_option_msg()
            user_input = input(ui.CHOOSE_MENU_OPTION)
        return int(user_input)

    @staticmethod
    def incorrect_option_msg():
        ui.show_msg(ui.UNKNOWN_OPTION)
        ui.show_msg(ui.SEPARATOR)

    def open_menu_option(self, option):
        if option == ui.ServerMenu.add_terminal.number:
            self.show_add_terminal_ui()
        elif option == ui.ServerMenu.exit_menu.number:
            self.__server_active = False
        elif option == ui.ServerMenu.remove_terminal.number:
            self.show_remove_terminal_ui()
        elif option == ui.ServerMenu.add_worker.number:
            self.show_add_worker_ui()
        elif option == ui.ServerMenu.remove_worker.number:
            self.show_remove_worker_ui()
        elif option == ui.ServerMenu.add_card_to_worker.number:
            self.show_assign_card_ui()
        elif option == ui.ServerMenu.remove_worker_card.number:
            self.show_unassign_card_ui()
        elif option == ui.ServerMenu.show_workers.number:
            self.show_data(self.server.get_workers().values())
        elif option == ui.ServerMenu.show_logs.number:
            self.show_data(self.server.get_logs().values())
        elif option == ui.ServerMenu.show_terminals.number:
            self.show_data(self.server.get_terminals().values())
        elif option == ui.ServerMenu.generate_reports.number:
            self.show_reports_generate_menu()
        elif option == ui.ServerMenu.tracking_activity.number:
            self.show_tracking_activity_menu()
        else:
            self.incorrect_option_msg()
        ui.read_data(ui.WAIT_FOR_INPUT)

    @staticmethod
    def read_literal(prompt):
        literal = ui.read_data(prompt)
        while any(char.isdigit() for char in literal) or len(literal.strip()) < 2:
            ui.show_msg(ui.INCORRECT_LITERALS_INPUT)
            literal = ui.read_data(prompt)
        return literal.upper()

    @staticmethod
    def read_digit(prompt):
        digit = ui.read_data(prompt)
        while not digit.isdigit():
            ui.show_msg(ui.INCORRECT_DIGIT_INPUT)
            digit = ui.read_data(prompt)
        return digit

    def show_add_terminal_ui(self):
        term_guid = ServerController.read_digit(ui.TERM_GUID_INPUT)
        term_name = ui.read_data(ui.TERM_NAME_INPUT)
        try:
            self.server.add_term(term_guid, term_name)
        except DataInputError as err:
            ui.show_msg(err.message)
        else:
            ui.show_msg(ui.ADDED_TERM)

    def show_remove_terminal_ui(self):
        term_guid = ui.read_data(ui.TERM_GUID_INPUT)
        try:
            self.server.remove_term(term_guid)
        except DataInputError as err:
            ui.show_msg(err.message)
        else:
            ui.show_msg(ui.REMOVED_TERM)

    def show_add_worker_ui(self):
        worker_guid = ServerController.read_digit(ui.WORKER_ID_INPUT)
        worker_name = ServerController.read_literal(ui.WORKER_NAME_INPUT)
        worker_surname = ServerController.read_literal(ui.WORKER_SURNAME_INPUT)

        try:
            self.server.add_worker(worker_name, worker_surname, worker_guid)
        except DataInputError as err:
            ui.show_msg(err.message)
        else:
            ui.show_msg(ui.ADDED_WORKER)

    def show_remove_worker_ui(self):
        worker_id = ui.read_data(ui.WORKER_ID_INPUT)
        try:
            self.server.remove_worker(worker_id)
        except DataInputError as err:
            ui.show_msg(err.message)
        else:
            ui.show_msg(ui.REMOVED_WORKER)

    def show_assign_card_ui(self):
        worker_guid = ui.read_data(ui.WORKER_ID_INPUT)
        card_guid = ServerController.read_digit(ui.CARD_ID_INPUT)
        try:
            self.server.assign_card(card_guid, worker_guid)
        except DataInputError as err:
            ui.show_msg(err.message)
        else:
            ui.show_msg(ui.ADDED_CARD)

    def show_unassign_card_ui(self):
        term_id = ui.read_data(ui.CARD_ID_INPUT)
        try:
            worker_id = self.server.unassign_card(term_id)
        except DataInputError as err:
            ui.show_msg(err.message)
        else:
            ui.show_msg(ui.REMOVED_CARD + worker_id)

    @staticmethod
    def show_data(list_to_show):
        ui.show_msg(ui.SEPARATOR)
        if list_to_show.__len__() > 0:
            for element in list_to_show:
                ui.show_msg(element.__str__())
                ui.show_msg(ui.SEPARATOR)
        else:
            ui.show_msg(ui.EMPTY)
            ui.show_msg(ui.SEPARATOR)

    def show_reports_generate_menu(self):
        ui.ServerReportsMenu.show()
        option = ServerController.get_menu_option()
        if option == ui.ServerReportsMenu.report_log_from_day.number:
            self.log_from_day()
        elif option == ui.ServerReportsMenu.report_log_from_day_worker.number:
            self.log_from_day_for_worker()
        elif option == ui.ServerReportsMenu.report_work_time_from_day_worker.number:
            self.work_time_from_day_for_worker()
        elif option == ui.ServerReportsMenu.report_work_time_from_day.number:
            self.work_time_from_day()
        elif option == ui.ServerReportsMenu.report_general_work_time.number:
            self.show_worker_with_time_report(self.server.general_report(True))
        else:
            self.incorrect_option_msg()

    def log_from_day(self):
        date = self.read_player_date_input()
        if date is not None:
            generated_data = self.server.report_log_from_day(True, date)
            self.show_data(generated_data)

    def log_from_day_for_worker(self):
        worker_id = ui.read_data(ui.WORKER_ID_INPUT)
        date = self.read_player_date_input()
        if date is not None:
            generated_data = self.server.report_log_from_day_worker(worker_id, True, date)
            self.show_data(generated_data)

    def work_time_from_day_for_worker(self):
        worker_id = ui.read_data(ui.WORKER_ID_INPUT)
        date = self.read_player_date_input()
        if date is not None:
            generated_data = self.server.report_work_time_from_day_worker(worker_id, date)
            ui.show_msg(ui.SEPARATOR)
            ui.show_msg(generated_data)
            ui.show_msg(ui.SEPARATOR)

    def work_time_from_day(self):
        date = self.read_player_date_input()
        if date is not None:
            generated_data = self.server.report_work_time_from_day(True, date)
            self.show_worker_with_time_report(generated_data)

    def show_tracking_activity_menu(self):
        self.tracking_activity = True
        ui.show_msg(ui.TRACKING_ACTIVITY_MENU)
        ui.show_msg(ui.SEPARATOR)
        user_input = input()
        while user_input != "0":
            user_input = input()
        self.tracking_activity = False

    @staticmethod
    def show_worker_with_time_report(tuple_list):
        ui.show_msg(ui.SEPARATOR)
        for tup in tuple_list:
            ui.show_msg("Worker GUID: " + tup[0] + " Work time: " + tup[1].__str__())
            ui.show_msg(ui.SEPARATOR)

    @staticmethod
    def read_player_date_input():
        date_str = ui.read_data(ui.DATE_INPUT)
        if date_str == "":
            return datetime.now()
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            return date
        except ValueError:
            ui.show_msg(ui.INCORRECT_DATE_FORMAT + datetime.now().date().__str__())
            return None
