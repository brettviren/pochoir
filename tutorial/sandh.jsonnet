// Compile to a JSON file which serves as a config for
// pochoir gen -g sandh [...] cfg.json

local plane(axis, height, thick, potential=null, strips=null, holes=null) =
std.prune(
{
    axis:axis, height:height, thick:thick,
    potential:potential, strips:strips, holes:holes
});

local strips(paxis, pitch, gap, offset=0.0, weighting=false) =
{
    paxis:paxis, pitch:pitch, gap:gap, offset:offset, weighting:weighting
};

local holes(radius, spacing, offset=[0.0,0.0]) =
{
    radius:radius, spacing:spacing, offset:offset
};

local sandh(planes, ambient=0.0) = {
    planes: planes, ambient: ambient
};


// distance units are mm.  Bias are w.r.t. nominal drift
function(efield=50, cat_at=100, pcb_at=30, pcb_thick=3, pln_thick=0.1,
         ind_bias=0.0, col_bias=0.0, paxis=1, pitch=5.0, gap=0.2,
         strip_offset=0.0, weighting=false,
         hole_radius=2.0, hole_spacing=[5.0,5.0], hole_offset=[0.0,0.0],
         ambient=0.0)
{
    local ind_at = pcb_at + 0.5*pcb_thick,
    local col_at = pcb_at - 0.5*pcb_thick,
    
    planes: [
        // ground
        plane(0, 0, pln_thick, 0),
        // cathode
        plane(0, cat_at, pln_thick, efield*cat_at),
        // induction
        plane(0, ind_at, pln_thick, efield*ind_at+ind_bias,
              strips(paxis, pitch, gap, strip_offset, weighting),
              holes(hole_radius, hole_spacing, hole_offset)),
        // collection
        plane(0, col_at, pln_thick, efield*col_at+col_bias,
              strips(paxis, pitch, gap, strip_offset, weighting),
              holes(hole_radius, hole_spacing, hole_offset)),
    ],
    ambient:ambient,
}

    
