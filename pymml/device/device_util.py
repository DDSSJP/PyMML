from ..define import DeviceType
from .FT232H import FT232H
from .mock_device import MockDevice, MockDevice4

_device_type_cls_dic = {
    DeviceType.MOCK: MockDevice,
    DeviceType.MOCK4: MockDevice4,
    DeviceType.FT232H: FT232H,
}
_device_cls_type_dic = {
    MockDevice: DeviceType.MOCK,
    MockDevice4: DeviceType.MOCK4,
    FT232H: DeviceType.FT232H,
}

def device_type_to_cls(type):
    if type in _device_type_cls_dic.keys():
        return _device_type_cls_dic[type]
    raise Exception(f"Unknown device type -> {str(type)}")

def device_cls_to_type(cls):
    if cls in _device_cls_type_dic.keys():
        return _device_cls_type_dic[cls]
    raise Exception(f"Unknown device class -> {str(cls)}")

def device_search(show=False, save=False):
    info_list = []
    for device_type in DeviceType.get_list():
        if device_type == DeviceType.UNKNOWN:
            continue
        info_list.extend(device_type_to_cls(device_type).search())

    if show:
        if len(info_list) == 0:
            print("not found device.")
            return
        print(f"found devices.")
        for info in info_list:
            print("   ", info)
        print()
    
    if save:
        import json
        import datetime
        dic = {}
        dic["output datetime"] = str(datetime.datetime.now())
        dic["device_info_list"] = []
        for i in range(len(info_list)):
            dic["device_info_list"].append(
                {"DeviceType":info_list[i].device_type,
                 "DeviceID":info_list[i].device_id,
                 "detail":info_list[i].detail})
        with open("device_info_list.json","w") as f:
            f.write(json.dumps(dic,ensure_ascii=False,indent=4))

    return info_list
