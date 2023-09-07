/**
 * A map control panel for GeoJSON data layers and base tilesets.
 */

"use client";

import Checkbox from "@/components/Checkbox";
import RadioButton from "@/components/RadioButton";
import { useState } from "react";
import { useSnapshot } from "valtio";

function MapControlPanel({
    snap,
    isLayerToggled,
    shouldDisableLayer,
    selectAllToggableLayers,
    clearToggableLayers,
    handleLayerChecked,
    setBasemap
 }) {

    const [expanded, setExpanded] = useState(true);

    return (
        <div className="w-full max-w-xs mx-auto">

            {/** TITLE */}
            <h5 className="text-center">Select Layers</h5>

            {/** MENU */}
            <div className={`form-control h-0 overflow-hidden items-start ${expanded && "h-auto overflow-auto max-h-full"}`}>

                {/** SECTION DIVIDER */}
                <div className="divider m-0"></div>

                {/** DATA LAYER CHECKBOXES */}
                {snap.layers.toggleOptions.map((option, index) => {
                    return <Checkbox
                        key={index}
                        option={option}
                        checked={isLayerToggled(option)}
                        disabled={shouldDisableLayer(option)}
                        onClick={handleLayerChecked}
                    />
                })}

                {/** DATA LAYER BULK OPERATION BUTTONS */}
                <div className="join justify-center py-2">
                    <button
                        className="btn join-item btn-sm normal-case"
                        onClick={(_) => selectAllToggableLayers()}
                    >
                        All
                    </button>
                    <button
                        className="btn join-item btn-sm normal-case"
                        onClick={(_) => clearToggableLayers()}
                    >
                        None
                    </button>
                </div>

                {/** SECTION DIVIDER */}
                <div className="divider m-0"></div>

                {/** BASE MAP RADIO BUTTONS */}
                {Object
                    .entries(snap.basemap.options)
                    .map(([mapType, settings], index) => (
                        <RadioButton
                            key={index}
                            option={mapType}
                            name={settings.name}
                            isChecked={settings.name == snap.basemap.selected.name}
                            onChange={setBasemap}
                        />
                ))}
            </div>

            {/** MENU TOGGLE BUTTON */}
            <div className="flex justify-center py-2">
                <button
                    className="btn btn-sm normal-case"
                    onClick={() => setExpanded((e) => !e)}
                >
                    {expanded ? "Collapse Menu" : "Show Menu"}
                </button>
            </div>
        </div>
    );
}

export default MapControlPanel;