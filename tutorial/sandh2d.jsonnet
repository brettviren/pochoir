local mm = 1.0;                 // match pochoir.units.mm
local cm = 10*mm;
local V = 1.0;

local pitch = 5*mm;
local thick = 0.1*mm;
local gap = 0.1*mm;
local sep = 3.2*mm;

local indy = 20*mm;
local coly = indy-sep;
local caty = 20*cm;
local gndy = 0*cm;

local efield = -500*V/cm;

local fullwidth = 11*pitch;
local fullheight = caty;
local gridspacing = 0.1*mm;

local centerline = 0.0*mm;

local domain_shape = [fullwidth/gridspacing,
                      fullheight/gridspacing];

local domain = {
    shape: [std.parseInt("%d"%d) for d in domain_shape],
    spacing: gridspacing,
};

local anode(loc, pot, isw) = {
    pitch: pitch,
    thick: thick,
    gap: gap,
    location: loc,
    voltage: pot,
    weighting: isw,
};


local plane(loc, pot, isw) = {
    pitch: fullwidth,
    thick: thick,
    gap: 0.0,
    location: loc,
    voltage: pot,
    weighting: isw,
};

local drift_planes = [
    plane(caty, caty*efield, false),
    anode(indy, 0*V, false),
    anode(coly, 1000*V, false),
    plane(gndy, 0.0*V, false),
];
local weight0_planes = [
    plane(caty, 0.0*V, true),
    anode(indy, 1.0*V, true),
    anode(coly, 0.0*V, true),
    plane(gndy, 0.0*V, true),
];
local weight1_planes = [
    plane(caty, 0.0*V, true),
    anode(indy, 0.0*V, true),
    anode(coly, 1.0*V, true),
    plane(gndy, 0.0*V, true),
];

local gen1(plns) = {
    centerline: centerline,
    planes: plns
};

{
    "drift.json": gen1(drift_planes),
    "weight-ind.json": gen1(weight0_planes),
    "weight-col.json": gen1(weight1_planes),
    "domain.json": domain,
}
