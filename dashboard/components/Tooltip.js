/**
 * A tooltip to use for deck.gl map layers.
 */

"use client";

import React from "react";

const Tooltip = React.memo(({ hoverInfo }) => {
        return (
            <div 
                className="z-10 py-10 text-xs bg-slate-50 absolute"
                style={{left: hoverInfo.x, top: hoverInfo.y}}
            >
                <h1>{hoverInfo.name}</h1>
            </div>
        );
    }
);

export default Tooltip;
