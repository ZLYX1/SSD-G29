from data_sources.user_record_set import UserRecordSet


class UnitOfWork:
    def __init__(self):
        self.session = None
        self.users = UserRecordSet(self.session)
