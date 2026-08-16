def is_bool(value):
    if type(value) == int:
        return value == 0 or value == 1
    if type(value) == str:
        value = value.strip().lower()
        return value in ["false","true","0","1"]
    return False

def is_int(value):
    try:
        int(value)
    except:
        return False
    return True

def is_float(value):
    try:
        float(value)
    except:
        return False
    return True

def is_range(minv, maxv, value):
    if minv is not None and minv > value:
        return False
    if maxv is not None and maxv < value:
        return False
    return True

def check(name, value, typ, minv=None, maxv=None):
    msg = ""
    if type(typ) == list or type(typ) == tuple:
        if value not in typ:
            msg = f"{name} : unknown value. ({typ})"
    elif typ == int:
        if not is_int(value):
            msg = f"{name} : cannot be converted to int."
    elif typ == float:
        if not is_float(value):
            msg = f"{name} : cannot be converted to float."
    elif typ == bool:
        if not is_bool(value):
            msg = f"{name} : cannot be converted to bool."
    elif type(typ) == str and type(value) == str:
        for c in value:
            if c not in typ:
                msg = f"{name} : find invarit char -> {c} ({typ})"
    if len(msg) == 0:
        if typ == int or typ == float:
            if minv is not None or maxv is not None:
                v = typ(value)
                if not is_range(minv, maxv, v):
                    msg = f"{name} : out of range. "
                    if minv is not None and maxv is not None:
                        msg += f" ({minv} <= value <= {maxv})"
                    elif minv is None and maxv is not None:
                        msg += f" (value <= {maxv})"
                    elif minv is not None and maxv is None:
                        msg += f" ({minv} <= value)"
    return msg
