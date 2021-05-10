// Meta configuration file.

// Each type of object has a name and we build an objected keyed by
// that name so we may reference names as keys and avoid
// spelling. (DRY pattern).
local byname(lst) = { [o.name]:o for o in lst };

// Describe a grid of points
local domains = byname([
    {
        name: "elects3d",
        cfg: {
            shape:"84,56,1000",
            spacing:"0.1*mm"
        }
    },
    {
        name: "weight2d",
        cfg: {
            shape:"1092,2500",
            spacing:"0.1*mm"
        },
    },
    {
        name: "weight3d",
        cfg: {
            shape:"350,66,2000",
            spacing:"0.1*mm"
        },
    },

]);


// Describe geometry "generators"
local generators = byname([
    {
        name: "drift3d",
        domain: domains.elects3d.name,
        method: "pcb_quarter",
        cfg: {
            FirstHoleRadius : "1.25*mm",
            SecondHoleRadius : "1.25*mm",
            PcbWidth : "3.2*mm",
            PcbLowEdgePosition : "17*mm",
            CathodePotential : "2000*V",
            AnodePotential : "-15000*V"
        }
    },
    {
        name: "weight2d0",
        domain: domains.weight2d.name,
        method: "pcb_2D",
        cfg: {
            plane : 0,
            config : 1,
            StripWidthX : "5.2*mm",
            StripWidthZ : "3.2*mm",
            HoleDiameter : "2.5*mm",
            LowEdgePosition : "17*mm",
            Nstrips : 21
        },
    },
    {
        name: "weight3d0",
        domain: domains.weight3d.name,
        method: "pcb_3D",
        cfg: {
            plane : 0,
            FirstHoleRadius : "1.25*mm",
            SecondHoleRadius : "1.25*mm",
            PcbWidth : "3.2*mm",
            PcbLowEdgePosition : "17*mm",
            Nstrips : 7,
            QuarterDimX : "2.5*mm",
            QuarterDimY : "1.67*mm"
        }
    },
]);

// Describe a field problem
local fields = byname([
    {
        name: "drift",
        generator: generators.drift3d.name,
        domain: domains.elects3d.name,
        cfg: {
            edges:"per,per,per",
            precision:0.2,
            epoch:200,
            nepochs:200
        },
    },
    
    {
        name: "weight2d0",
        generator: generators.weight2d0.name,
        domain: domains.weight2d.name,
        cfg: {
            edges:"per,per",
            precision:0.0002,
            epoch:10,
            nepochs:10
        },

    },

    {
        name: "weight3d0",
        generator: generators.weight3d0.name,
        domain: domains.weight3d.name,
        cfg: {
            edges:"per,per,per",
            precision:0.0002,
            epoch:10,
            nepochs:10
        },
    }
]);

local drifts = byname([
    {
        name: "induction",
        field: fields.drift.name,
        domain: fields.drift.domain,
        generator: fields.drift.generator,
        cfg: {
            points: [["1.25*mm", "0.835*mm", "29.0*mm"]],
            steps: ["0", "150*us", "0.1*us"]
        }
    },
]);

local meta(taxon, objects) = {
    [taxon + ".json"]: {[o.name]:std.prune(o{cfg:null}) for o in objects}
};

local cfg(taxon, objects) = {
    [taxon+'-'+o.name+'.json']: o.cfg for o in objects
};

local everything = {
    domains: domains, generators: generators,
    fields: fields, drifts: drifts
};

local both(name, group) = {
    local objects = std.objectValues(group),
    ret: meta(name+"s", objects) + cfg(name, objects)
}.ret;

    
both("domain", domains) + both("generator", generators) +
    both("field", fields) + both("drift", drifts)
