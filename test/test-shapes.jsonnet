
local rectangle(name, pt1, pt2) = {
    type:"rectangle",
    name:name,
    point1:pt1,
    point2:pt2,
};
local circle(name, rad, cen) = {
    type:"circle",
    name:name,
    radius: rad,
    center: cen,
};

{
    shapes: [
        rectangle("strip%d"%s, [s*5-2, 0],[s*5-2, 10]),
        for s in [0,1,2]
        ] + [
        circle("holeA%d"%s, 2, [s*5-2.5, 0]),
        for s in [0,1,2]
        ] + [ 
        circle("holeB%d"%s, 2, [s*5-2.5, 10])
        for s in [0,1,2]
        ],
    values: {
        ["strip%d"%s]:100 for s in [0,1,2]
    },
}
