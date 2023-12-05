/**
 * Configuration for Deck GL GeoJSON map layers.
 */

const layerConfig = [
    {
        externalId: "low_income",
        id: "Low Income Census Tracts",
        mapboxTilesetId: "launa-greer.cc-low-income",
        fillColor: [255, 0, 0],
        opacity: 0.1,
        canToggle: true,
        initialVisibility: true
    },
    {
        externalId: "justice40",
        id: "Justice 40 Communities",
        mapboxTilesetId: "launa-greer.cc-justice40",
        fillColor: [255, 255, 153],
        opacity: 0.1,
        canToggle: true,
        initialVisibility: true
    },
    {
        externalId: "distressed",
        id: "Distressed Communities",
        mapboxTilesetId: "launa-greer.cc-distressed",
        fillColor: [153, 0, 153],
        opacity: 0.1,
        canToggle: true,
        initialVisibility: true
    },
    {
        externalId: "energy",
        id: "Energy Communities",
        mapboxTilesetId: "launa-greer.cc-energy",
        fillColor: [0, 153, 0],
        opacity: 0.1,
        canToggle: true,
        initialVisibility: true
    },
    {
        externalId: "municipal_util",
        id: "Municipal Utilities",
        mapboxTilesetId: "launa-greer.cc-municipal-utils",
        fillColor: [255, 255, 100],
        opacity: 0.1,
        canToggle: false,
        initialVisibility: true
    },
    {
        externalId: "rural_coop",
        id: "Rural Co-Ops",
        mapboxTilesetId: "launa-greer.cc-rural-coops",
        fillColor: [255, 255, 100],
        opacity: 0.1,
        canToggle: false,
        initialVisibility: true
    },
    {
        externalId: "county",
        id: "Counties",
        mapboxTilesetId: "launa-greer.cc-counties",
        fillColor: [0, 0, 0],
        opacity: 0.1,
        canToggle: true,
        initialVisibility: false
    },
    {
        externalId: "state",
        id: "States",
        mapboxTilesetId: "",
        fillColor: [0, 0, 0],
        opacity: 0,
        canToggle: false,
        initialVisibility: false
    }
];

export { layerConfig };