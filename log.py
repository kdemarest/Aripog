import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
log.addHandler(console_handler)
