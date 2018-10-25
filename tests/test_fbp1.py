from fbp import fbppool


if __name__ == '__main__':
    app = fbppool.App('../fbp.config', '', '')

    app.start_flows()

    while True:
        x = 1

