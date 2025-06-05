from project import create_app,socket

app = create_app()

if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch()
    socket.run(app,debug=True, port=5000, host='0.0.0.0')