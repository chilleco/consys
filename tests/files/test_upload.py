from . import uploader


def test_simple():
    data = uploader.image(
        'data:image/jpeg;base64,/9j/2wCEABQQEBkSGScXFycyJh8mMi4mJiYmLj41NTU1NT5EQUFBQUFBREREREREREREREREREREREREREREREREREREREQBFRkZIBwgJhgYJjYmICY2RDYrKzZERERCNUJERERERERERERERERERERERERERERERERERERERERERERERERERP/dAAQABP/uAA5BZG9iZQBkwAAAAAH/wAARCAA5ADkDACIAAREBAhEB/8QAdQAAAgMBAQAAAAAAAAAAAAAABAUBAwYCAAEBAQEBAAAAAAAAAAAAAAAAAQACAxAAAgECBQEGBgIDAAAAAAAAAQIDABEEEiExQVEFEyJhcZEUMlKBwfAVQrHR4REBAQEBAQEBAQAAAAAAAAAAAAERMQIhQXH/2gAMAwAAARECEQA/AM/8TNKSUY77XomBJsRC0sMhEqHxC+4P7p7UtTwetH9hyPHig6LmuCrDyNTnOg/jJXYCUknbWiVRXcK2tFdt4RMPLY3DHxI34P8AulTqwNwbsdQB060dP6mWLI5Xa1e7sgX4qQrBgz34PvROGwD4yUK11B2Xn/lOs5oIgiouetantPBQYLDmyjXwDTk1m/hT9QqL/9DM5SaOwK95G4UgEfmgj6UT2eLuyf2tdQefKi7jEy1GMvlCFiSBpVKIjyWvoBlvRuFvPIqSR5WBNtwQfvx/iuoeznUMcpzHShWWKcFiiGBdbAklT++VarBzYRFz5rNuS1IIRhUASWQF0Ni1iPQDrXUsudgS2g0GXmhrnVmPlkkJAKmNSxA5PFz6cdaWZaMDllaw0G531oXuz0FMFf/RztgeRUqzQussZGZTepyg8V2pCfKBfqeKPgz22Ix3fwF1sHtzwaqikEosm1rMTSHA41lugXOOFY6n79fKmkGLw76qrK3I2rFjr59STL1xiuzsPlDxoMw2DXNUw4TNdmAvyW2tTRy5W8aXPBJ460FjFOXNiHAUHRV3ar+ud+8DYmdHtHFqo5HJ/eKrySfSfaiWVox3jrlJB7tfpHn50L38nWmbRuP/0keHwzSIGdZAWtYoyaj0NScKyta0muq+JPlHzc+1KDv7VHFQyHS4YFhl72+ut49wfXSr5ZJ2BzNITcKtzHbXr+DWerwqLRK0ysqI0wve3ijta3rb7Gg5p2whzZpBiDY3JRl/NK12Nc1Yhb9pYlzdpCSa5/kMR9ZoapqT/9k='
    )

    assert data[:3] == '000'
    assert data[-5:] == '.jpeg'

def test_png():
    data = uploader.image(
        'data:image/png;base64,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'
    )

    assert data[:3] == '000'
    assert data[-4:] == '.png'