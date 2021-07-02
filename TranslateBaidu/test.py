import execjs


def main():
    with open("code.js", "r") as fp:
        js_data = fp.read()
    sign = execjs.compile(js_data).call("e", "translate")
    print(sign)


if __name__ == '__main__':
    main()