class RegistryLog:
    def __init__(self, time, term_guid, card_guid, worker_guid=None):
        self.time = time
        self.term_guid = term_guid
        self.card_guid = card_guid
        self.worker_guid = worker_guid

    def __str__(self):
        time_msg = "Time: " + self.time + "\n"
        term_msg = "Terminal GUID: " + self.term_guid + "\n"
        if self.worker_guid is None:
            worker_msg = "Worker GUID: unknown (not registered)\n"
        else:
            worker_msg = "Worker GUID: " + self.worker_guid + "\n"
        card_msg = "Card GUID: " + self.card_guid
        return time_msg + term_msg + worker_msg + card_msg
