local mm = 1.0;                 // match pochoir.units.mm
local cm = 10*mm;
local V = 1.0;

local pitch = 5*mm;
local thick = 0.1*mm;
local diameter = 2.5*mm;
local gap = 0.2*mm;
//local gap = 1*mm;
local sep = 3.2*mm;

local indy = 20*mm;
local coly = indy-sep;
local caty = 20*cm;
local gndy = 0*cm;

local efield = -500*V/cm;

local drift_width = pitch;
local weight_width = 11*pitch;
local full_height = caty;
local gridspacing = 0.1*mm;
//local gridspacing = 1*mm;

local centerline = 0.0*mm;

local domain(width, height) = {
    shape:[std.parseInt("%d"%(d/gridspacing)) for d in [height,width]],
    spacing: gridspacing,
    origin: [0, -0.5*width],
};    

local anode(name, loc, pot, isw) = {
    name: name,
    pitch: pitch,
    thick: thick,
    diameter: diameter,
    gap: gap,
    location: loc,
    voltage: pot,
    weighting: isw,
};


local plane(name, loc, pot, isw) = {
    name: name,
    pitch: if isw then weight_width else drift_width,
    thick: thick,
    gap: 0.0,
    location: loc,
    voltage: pot,
    weighting: isw,
};

local drift_planes = [
    plane("cat", caty, caty*efield, false),
    anode("ind", indy, 0*V, false),
    anode("col", coly, 1000*V, false),
    plane("gnd", gndy, 0.0*V, false),
];
local weight0_planes = [
    plane("cat", caty, 0.0*V, true),
    anode("ind", indy, 1.0*V, true),
    anode("col", coly, 0.0*V, true),
    plane("gnd", gndy, 0.0*V, true),
];
local weight1_planes = [
    plane("cat", caty, 0.0*V, true),
    anode("ind", indy, 0.0*V, true),
    anode("col", coly, 1.0*V, true),
    plane("gnd", gndy, 0.0*V, true),
];

local gen1(plns) = {
    centerline: centerline,
    planes: plns
};

{
    "drift.json": gen1(drift_planes),
    "weight-ind.json": gen1(weight0_planes),
    "weight-col.json": gen1(weight1_planes),
    "domains/drift.json": domain(drift_width, full_height),
    "domains/weight.json": domain(weight_width, full_height),
}
