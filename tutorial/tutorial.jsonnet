local sandh = import "sandh.jsonnet";

local domains = [
    {
        name: "wfar",
        shape: "1051,1051",
        spacing: 0.1
    },
];

local gens = [
    {
        name: "sandh",
        
    } + sandh(),
];


{
    ["doms/%s.json"%d.name]: d for d in domains
} + {
    ["gens/%s.json"%g.name]: g for g in gens
}
    
