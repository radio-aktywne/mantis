from hashlib import md5


def hashify(x: str) -> int:
    digest = md5(x.encode("utf-8")).hexdigest()
    return int(digest, 16)
