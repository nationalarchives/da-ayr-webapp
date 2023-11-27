class TransferringBody:
    def __init__(self, body_id, body_name, body_description):
        self._body_id = body_id
        self._body_name = body_name
        self._body_description = body_description

    @property
    def body_id(self):
        return self._body_id

    @body_id.setter
    def body_id(self, value):
        self.body_id = value

    @property
    def body_name(self):
        return self._body_name

    @body_name.setter
    def body_name(self, value):
        self._body_name = value

    @property
    def body_description(self):
        return self._body_description

    @body_description.setter
    def body_description(self, value):
        self._body_description = value
