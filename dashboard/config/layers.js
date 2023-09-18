/**
 * Configuration for Deck GL GeoJSON map layers.
 */

const layerConfig = [
    {
        externalId: "low_income",
        id: "Low Income Census Tracts",
        fillColor: [255, 0, 0],
        opacity: 0.2,
        canToggle: true
    },
    {
        externalId: "justice40",
        id: "Justice 40 Communities",
        fillColor: [255, 51, 51, 255],
        opacity: 0.5,
        canToggle: true
    },
    {
        externalId: "distressed",
        id: "Distressed Communities",
        fillColor: [153, 0, 153, 255],
        opacity: 0.5,
        canToggle: true
    },
    {
        externalId: "energy",
        id: "Energy Communities",
        fillColor: [0, 153, 0, 255],
        opacity: 0.5,
        canToggle: true
    },
    {
        externalId: "municipal_util",
        id: "Municipal Utilities",
        fillColor: [255, 255, 100, 255],
        opacity: 0.5,
        canToggle: true
    },
    {
        externalId: "rural_coop",
        id: "Rural Co-Ops",
        fillColor: [255, 255, 100, 255],
        opacity: 0.5,
        canToggle: false
    },
    {
        externalId: "county",
        id: "Counties",
        fillColor: [0, 0, 0, 255],
        opacity: 0.2,
        canToggle: true
    },
    {
        externalId: "state",
        id: "States",
        fillColor: [0, 0, 0, 255],
        opacity: 0,
        canToggle: false
    }
];

export { layerConfig };
