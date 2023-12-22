/**
 * Configuration for Deck GL GeoJSON map layers.
 * NOTE: The order of the items here will determine
 * the order of the DeckMVT tileset layers, which
 * affects what is displayed by the tooltip on hover. 
 */

const layerConfig = [
    {
        externalId: "state",
        id: "States",
        mapboxTilesetName: "cc_states",
        fillColor: [0, 0, 0],
        opacity: 0,
        canToggle: false,
        initialVisibility: false
    },
    {
        externalId: "county",
        id: "Counties",
        mapboxTilesetName: "cc_counties",
        fillColor: [0, 0, 0],
        opacity: 0.1,
        canToggle: true,
        initialVisibility: true
    },
    {
        externalId: "rural cooperative",
        id: "Rural Co-Ops",
        mapboxTilesetName: "cc_rural_coops",
        fillColor: [209, 29, 84],
        opacity: 0.1,
        canToggle: false,
        initialVisibility: true
    },
    {
        externalId: "municipal utility",
        id: "Municipal Utilities",
        mapboxTilesetName: "cc_municipal_utils",
        fillColor: [209, 29, 84],
        opacity: 0.1,
        canToggle: false,
        initialVisibility: true
    },
    {
        externalId: "municipality",
        id: "Municipalities",
        mapboxTilesetName: "cc_municipalities",
        fillColor: [209, 29, 84],
        opacity: 0.1,
        canToggle: false,
        initialVisibility: true
    },
    {
        externalId: "distressed",
        id: "Distressed Communities",
        mapboxTilesetName: "cc_distressed",
        fillColor: [153, 0, 153],
        opacity: 0.1,
        canToggle: true,
        initialVisibility: true
    },
    {
        externalId: "energy",
        id: "Energy Communities",
        mapboxTilesetName: "cc_energy",
        fillColor: [0, 153, 0],
        opacity: 0.1,
        canToggle: true,
        initialVisibility: true
    },
    {
        externalId: "justice40",
        id: "Justice 40 Communities",
        mapboxTilesetName: "cc_justice40",
        fillColor: [174, 209, 29],
        opacity: 0.1,
        canToggle: true,
        initialVisibility: true
    },
    {
        externalId: "low-income",
        id: "Low Income Census Tracts",
        mapboxTilesetName: "cc_low_income",
        fillColor: [255, 0, 0],
        opacity: 0.1,
        canToggle: true,
        initialVisibility: true
    }
];

export { layerConfig };