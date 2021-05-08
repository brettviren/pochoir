
local domains = [
    { name:"elects3d", cfg: {shape:"84,56,1000", spacing:"0.1*mm" }},
    { name:"weight2d", cfg: {shape:"1092,2500", spacing:"0.1*mm" }},
    { name:"weight3d", cfg: {shape:"350,66,2000", spacing:"0.1*mm" }},
];

local fields = [
    {
        name: "drift",
        generator: "pcb_quarter",
        domain: "elects3d",
        fdmcfg: {
            edges:"per,per,per",
            precision:0.2,
            epoch:200,
            nepochs:200
        },
        gencfg: {
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
        generator: "pcb_2D",
        domain: "weight2d",
        fdmcfg: {
            edges:"per,per",
            precision:0.0002,
            epoch:10,
            nepochs:10
        },
        gencfg: {
            plane : 0,
            config : 1,
            StripWidthX : "5.2*mm",
            StripWidthZ : "3.2*mm",
            HoleDiameter : "2.5*mm",
            LowEdgePosition : "17*mm",
            Nstrips : 21
        }
    },
    {
        name: "weight3d0",
        generator: "pcb_3D",
        domain: "weight3d",
        fdmcfg: {
            edges:"per,per,per",
            precision:0.0002,
            epoch:10,
            nepochs:10
        },
        gencfg: {
            plane : 0,
            FirstHoleRadius : "1.25*mm",
            SecondHoleRadius : "1.25*mm",
            PcbWidth : "3.2*mm",
            PcbLowEdgePosition : "17*mm",
            Nstrips : 7,
            QuarterDimX : "2.5*mm",
            QuarterDimY : "1.67*mm"
        }
    }
];



{
    ["domain-"+d.name+".json"]: d.cfg for d in domains
} + {
    "domains.json": [d.name for d in domains]
} + {
    ["field-"+f.name+".json"]: f.gencfg for f in fields
} + {
    "fields.json": {[g.name]:{
        domain:g.domain,
        generator:g.generator,
        fdmcfg: g.fdmcfg
    } for g in fields}
}
    
