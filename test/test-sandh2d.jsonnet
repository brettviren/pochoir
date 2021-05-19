local mm = 1.0;                 // match pochoir.units.mm
local cm = 10*mm;
local V = 1.0;

local gridspacing = 0.1*mm;

local pitch = 5*mm;
local thick = 2*gridspacing;
local diameter = 2.5*mm;
local gap = 2*gridspacing;
//local gap = 1*mm;
local sep = 3.2*mm;

local indy = 20*mm;
local coly = indy-sep;
local caty = 20*cm - gridspacing;
//local gndy = 0*cm;
local gndy = gridspacing;

local efield = -500*V/cm;
local catv = caty*efield;
local indv = 0*V;
local colv = 1000*V;
local gndv = 0*V;

local drift_width = pitch;
local weight_width = 11*pitch;
local full_height = caty;
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

local drift = {
    centerline: centerline,
    planes: [
        plane("cat", caty, catv, false),
        anode("ind", indy, indv, false),
        anode("col", coly, colv, false),
        plane("gnd", gndy, gndv, false),
    ],
    fdm: {
        nepochs: 100,
        epoch: 1000,
        prec: 0.0001,
        edges: "fixed,periodic"
    },
};
local weight_fdm = {
    nepochs: 100,
    epoch: 100,
    prec: 0.01,
    edges: "fixed,periodic"
};
local weight0 = {
    centerline: centerline,
    planes: [
        plane("cat", caty, 0.0*V, true),
        anode("ind", indy, 1.0*V, true),
        anode("col", coly, 0.0*V, true),
        plane("gnd", gndy, 0.0*V, true),
    ],
    fdm: weight_fdm
};
local weight1 = {
    centerline: centerline,
    planes: [
        plane("cat", caty, 0.0*V, true),
        anode("ind", indy, 0.0*V, true),
        anode("col", coly, 1.0*V, true),
        plane("gnd", gndy, 0.0*V, true),
    ],
    fdm: weight_fdm    
};

local gen1(plns) = {

    planes: plns
};

{
    "gencfg/drift.json": drift,
    "gencfg/weight-ind.json": weight0,
    "gencfg/weight-col.json": weight1,
    "domains/drift.json": domain(drift_width, full_height),
    "domains/weight.json": domain(weight_width, full_height),
}
