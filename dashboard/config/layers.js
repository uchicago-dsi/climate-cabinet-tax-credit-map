/**
 * Configuration for Deck GL GeoJSON map layers.
 */

const layerConfig = [
    {
        externalId: "low_income",
        id: "Low Income Census Tracts",
        mapboxTilesetId: "launa-greer.cc-low-income",
        fillColor: [255, 0, 0],
        opacity: 0.2,
        canToggle: true
    },
    {
        externalId: "justice40",
        id: "Justice 40 Communities",
        mapboxTilesetId: "launa-greer.cc-justice40",
        fillColor: [255, 51, 51, 255],
        opacity: 0.5,
        canToggle: true
    },
    {
        externalId: "distressed",
        id: "Distressed Communities",
        mapboxTilesetId: "launa-greer.cc-distressed",
        fillColor: [153, 0, 153, 255],
        opacity: 0.5,
        canToggle: true
    },
    {
        externalId: "energy",
        id: "Energy Communities",
        mapboxTilesetId: "launa-greer.cc-energy",
        fillColor: [0, 153, 0, 255],
        opacity: 0.5,
        canToggle: true
    },
    {
        externalId: "municipal_util",
        id: "Municipal Utilities",
        mapboxTilesetId: "launa-greer.cc-municipal-utils",
        fillColor: [255, 255, 100, 255],
        opacity: 0.5,
        canToggle: false
    },
    {
        externalId: "rural_coop",
        id: "Rural Co-Ops",
        mapboxTilesetId: "launa-greer.cc-rural-coops",
        fillColor: [255, 255, 100, 255],
        opacity: 0.5,
        canToggle: false
    },
    {
        externalId: "county",
        id: "Counties",
        mapboxTilesetId: "launa-greer.cc-counties",
        fillColor: [0, 0, 0, 255],
        opacity: 0.2,
        canToggle: true
    },
    {
        externalId: "state",
        id: "States",
        mapboxTilesetId: "",
        fillColor: [0, 0, 0, 255],
        opacity: 0,
        canToggle: false
    }
];

export { layerConfig };