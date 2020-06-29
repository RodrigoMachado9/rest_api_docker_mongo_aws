from beartype import beartype


@beartype
def test(name: str):
    return 'hello %s' % name


print(test('machado'))
