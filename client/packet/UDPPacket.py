from constants.Constants import HEADER_VER_FIELD_KEY, HEADER_TYPE_FIELD_KEY, HEADER_TOKEN_LENGTH_FIELD_KEY, \
    HEADER_CLASS_STATUS_CODE_FIELD_KEY, HEADER_DETAIL_STATUS_CODE_FIELD_KEY, HEADER_TOKEN_FIELD_KEY, \
    HEADER_MESSAGE_ID_FIELD_KEY, HEADER_PAYLOAD_FIELD_KEY
from packet.CoapPacketHeader import CoapPacketHeader


class UDPPacket:
    def __init__(self):
        self.header = CoapPacketHeader()
        self.body = None

    def confirmable_packet(self, message_id, token, payload=''):
        # TODO:add options
        self.header \
            .ver(1) \
            .type(0) \
            .token_length(len(token)) \
            .class_status_code(0) \
            .detail_status_code(0) \
            .message_id(message_id) \
            .token(token) \
            .payload(payload)

        return self

    def non_confirmable_packet(self, message_id, token, payload=''):
        # TODO:add options
        self.header \
            .ver(1) \
            .type(1) \
            .token_length(len(token)) \
            .class_status_code(0) \
            .detail_status_code(0) \
            .message_id(message_id) \
            .token(token) \
            .payload(payload)

        return self

    def ACK_msg(self, message_id, token, payload=''):
        # TODO:add options
        self.header \
            .ver(1) \
            .type(2) \
            .token_length(len(token)) \
            .class_status_code(2) \
            .detail_status_code(0) \
            .message_id(message_id) \
            .token(token) \
            .payload(payload)

        return self

    def reset(self, message_id, token):
        # TODO:add options
        self.header \
            .ver(1) \
            .type(3) \
            .token_length(len(token)) \
            .class_status_code(0) \
            .detail_status_code(0) \
            .message_id(message_id) \
            .token(token) \
            .payload('')

        return self

    def serialize(self):
        if self.body:
            return bytes(self.header.msg_to_bytes()) + self.body
        return bytes(self.header.msg_to_bytes())

    # def __str__(self):
    #    return f'{self.header.content} -> {self.serialize()}'

    def __str__(self):
        return "\nVersion : " + str(self.header.content[HEADER_VER_FIELD_KEY]) + \
               "\nType : " + str(self.header.content[HEADER_TYPE_FIELD_KEY]) + \
               "\nToken_length : " + str(self.header.content[HEADER_TOKEN_LENGTH_FIELD_KEY]) + \
               "\nMessage_code : " + str(self.header.content[HEADER_CLASS_STATUS_CODE_FIELD_KEY]) + "." + str(
            self.header.content[HEADER_DETAIL_STATUS_CODE_FIELD_KEY]) + \
               "\nMessage_id : " + str(self.header.content[HEADER_MESSAGE_ID_FIELD_KEY]) + \
               "\nToken : " + str(self.header.content[HEADER_TOKEN_FIELD_KEY]) + \
               "\nPayload : " + str(self.header.content[HEADER_PAYLOAD_FIELD_KEY])
