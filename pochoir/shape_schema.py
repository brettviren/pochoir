def rectangle(name, point1, point2):
    if not all([point1, point2]):
        raise ValueError(f'rectangle "{name}" lacks points')
    return dict(type="rectangle", name=name,
                point1=point1, point2=point2)
