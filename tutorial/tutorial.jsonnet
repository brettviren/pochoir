
local domains = [
    {
        name: "wfar",
        shape: "1051,1051",
        spacing: 0.1
    },
];


{
    ["domains/%s.json"%d.name]: d for d in domains
}
