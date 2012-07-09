#!/usr/bin/python

import csv
import samsung

FILENAME = "/home/david/git/pySamsung/keycode_map.csv"

class ExitError(Exception):
    pass

def load(filename=FILENAME):
    res = {}
    f = open(filename)
    r = csv.DictReader(f, delimiter=';', quotechar='"')
    for data in r:
        key = res.setdefault(data["Category"], {}).setdefault(data["Key"], {})
        for (k, v) in (i for i in data.items() if i[0] not in ("Category", "Key")):
            key[k] = v
    f.close()
    return res

def save(data, filename=FILENAME):
    f = open(filename, "w")
    hdr = ("Category", "Key") + tuple(data.values()[0].values()[0].keys())
    print hdr
    w = csv.DictWriter(f, hdr, delimiter=";", quotechar='"')
    w.writeheader()
    for (cat, x) in data.items():
        for (key, info) in x.items():
            sd = {"Key": key, "Category": cat}
            sd.update(info)
            w.writerow(sd)
    f.close()

def get_choice(text, possible, exit="X"):
    res = None
    while not res in possible:
        print(text)
        print("Choices:")
        for p in possible:
            print("    %s" % p)
        res = raw_input("    ?: ")
        if res == exit:
            raise ExitError()
    print "choice: %s" % res
    return res

def main():
    data = load()
    categories = data.keys()
    devices = data.values()[0].values()[0].keys()
    
    try:
        while True:
            ip = raw_input("IP: ")
            device = get_choice("Device Name", devices)

            sd = samsung.Remote("pyremote", host=ip)
            category = get_choice("Key Category", categories)
            
            keys = data[category]
            for (key, d) in keys.items():
                if d[device]:
                    continue
                print("\nKey: %s" % key)
                
                text = "r"
                while text == "r":
                    try:
                        sd.send_key(key)
                    except:
                        pass
                    text = raw_input("Action [x=exit,r=retry]: ")
                    if text == "x":
                        raise ExitError()
                    elif text == "r":
                        continue
                    else:
                        d[device] = text
            res = get_choice("Category Done", ("exit", "continue"))
    except ExitError:
        pass
    save(data)

if __name__ == "__main__":
    main()
