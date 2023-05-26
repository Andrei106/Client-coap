import deprecated
from constants.Constants import HEADER_CONTENT, HEADER_VER_FIELD_KEY, HEADER_TYPE_FIELD_KEY, \
    HEADER_FIELD_LENGTH_MAPPINGS, \
    HEADER_MESSAGE_ID_FIELD_KEY, HEADER_TOKEN_FIELD_KEY, HEADER_OPTIONS_FIELD_KEY, HEADER_PAYLOAD_FIELD_KEY, \
    PAYLOAD_PADDING_VALUE, HEADER_TOKEN_LENGTH_FIELD_KEY, HEADER_DETAIL_STATUS_CODE_FIELD_KEY, \
    HEADER_CLASS_STATUS_CODE_FIELD_KEY, HEADER_NUMBER_BYTES


class CoapPacketHeader:
    def __init__(self):
        self.content = dict.fromkeys(HEADER_CONTENT, "")
        self.should_have_value = dict.fromkeys(HEADER_CONTENT, False)

    def ver(self, value):
        self.put(HEADER_VER_FIELD_KEY, value)
        return self

    def type(self, value):
        self.put(HEADER_TYPE_FIELD_KEY, value)
        return self

    def token_length(self, value):
        self.put(HEADER_TOKEN_LENGTH_FIELD_KEY, value)
        return self

    def class_status_code(self, value):
        self.put(HEADER_CLASS_STATUS_CODE_FIELD_KEY, value)
        return self

    def detail_status_code(self, value):
        self.put(HEADER_DETAIL_STATUS_CODE_FIELD_KEY, value)
        return self

    def message_id(self, value):
        self.put(HEADER_MESSAGE_ID_FIELD_KEY, value)
        return self

    def token(self, value):
        self.put(HEADER_TOKEN_FIELD_KEY, value)
        return self

    def options(self, value):
        self.put(HEADER_OPTIONS_FIELD_KEY, value)
        return self

    def payload(self, value):
        self.put(HEADER_PAYLOAD_FIELD_KEY, value)
        return self

    def put(self, key, value):
        #TODO: add validation
        self.content[key] = value
        for require_field in HEADER_CONTENT:
            self.should_have_value[require_field] = True
            if require_field == key:
                break

    @deprecated.deprecated(reason="use msg_to_bytes instead")
    def enhance_with_default_value(self, key):
        self.content[key] = ''.join([bin(0)[2:] for i in range(0, HEADER_FIELD_LENGTH_MAPPINGS[key])])

    @deprecated.deprecated(reason="use msg_to_bytes instead")
    def serialize(self):
        header = ''
        for header_field in self.content:
            if self.should_have_value[header_field]:
                if not self.content[header_field] or not len(self.content[header_field]):
                    self.enhance_with_default_value(header_field)
                field_value = ''
                if header_field == HEADER_PAYLOAD_FIELD_KEY:
                    if len(self.content[header_field]):
                        field_value = bin(PAYLOAD_PADDING_VALUE)[2:] + ''.join([bin(byte).strip('0b') for byte in bytes(self.content[header_field].encode('ascii'))])
                else:
                    field_value = bin(int(self.content[header_field]))[2:].zfill(HEADER_FIELD_LENGTH_MAPPINGS[header_field])
                header = header + field_value
        return header

    def msg_to_bytes(self):
        # TODO: add validation + options
        #research struct
        header = 0x00
        header |= int(self.content[HEADER_VER_FIELD_KEY]) << 0x1E
        header |= (0b11 & int(self.content[HEADER_TYPE_FIELD_KEY])) << 0x1C
        header |= (0xF & int(self.content[HEADER_TOKEN_LENGTH_FIELD_KEY])) << 0x18
        header |= (0b111 & int(self.content[HEADER_CLASS_STATUS_CODE_FIELD_KEY])) << 0x15
        header |= (0x1F & int(self.content[HEADER_DETAIL_STATUS_CODE_FIELD_KEY])) << 0x10
        header |= (0xFFFF & int(self.content[HEADER_MESSAGE_ID_FIELD_KEY]))
        if self.content[HEADER_TOKEN_LENGTH_FIELD_KEY]:
            header = (header << 8 * int(self.content[HEADER_TOKEN_LENGTH_FIELD_KEY])) | int(
                self.content[HEADER_TOKEN_FIELD_KEY])
        header = header.to_bytes(HEADER_NUMBER_BYTES + int(self.content[HEADER_TOKEN_LENGTH_FIELD_KEY]), 'big')
        payload = b''
        if len(self.content[HEADER_PAYLOAD_FIELD_KEY]):
            payload = bytes([PAYLOAD_PADDING_VALUE]) + self.content[HEADER_PAYLOAD_FIELD_KEY].encode()
        return header + payload


