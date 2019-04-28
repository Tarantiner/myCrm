from hashlib import md5


def to_md(data):
    md = md5(b'jfeoauofeijafjo')
    md.update(data.encode('utf-8'))
    return md.hexdigest()