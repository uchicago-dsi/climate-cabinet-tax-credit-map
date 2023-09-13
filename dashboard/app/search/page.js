/***
 * Renders a webpage for searching and viewing tax
 * credit benefit summaries for a geography.
 */

"use client"

import Autocomplete from "@/components/Autocomplete";
import ReportWidget from "@/components/ReportWidget";
import SummaryStats from "@/components/SummaryStats";
import { useState } from "react";


export default function SearchPage() {

    return (
        <div className="w-full p-5">
            <div className="flex flex-col items-center">
                <div className="text-left w-1/2">
                    <h2 className="text-center">Map Search Tool</h2>
                    <p className="py-5">
                        Enter the name of a state, county, municipality or rural electric
                        cooperative to view its Justice 40 communities, energy communities,
                        and designated low-income census tracts and MSAs on an interactive
                        map. The map will also show a description of available tax credit
                        programs.
                    </p>
                </div>
                {/** AUTOCOMPLETE SEARCH BAR */}
                <div className="relative m-2 z-50 w-1/2">
                    <div className="flex flex-row">
                        <Autocomplete />
                    </div>
                </div>
                    {/** REPORT WIDGET */}
                    <ReportWidget />
            </div>
        </div>
    )
    
}
