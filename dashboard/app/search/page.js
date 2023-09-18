/***
 * Renders a webpage for searching and viewing tax
 * credit benefit summaries for a geography.
 */

"use client"

import Autocomplete from "@/components/Autocomplete";
import ReportWidget from "@/components/ReportWidget";


export default function SearchPage() {

    return (
        <main className="w-screen">
            <div className="max-w-7xl mx-auto py-2">
                {/** HEADER  */}
                <div className="flex flex-col items-center">
                    {/** TITLE BANNER */}
                    <div
                        className="w-screen px-8 py-10 bg-center bg-cover bg-no-repeat"
                        style={{ backgroundImage: `url('/images/c3titlebanner2.jpg')` }}
                    >
                        <div className="container max-w-7xl mx-auto">
                            <h1 className="humani-title">Map Search Tool</h1>
                        </div>
                    </div>
                    {/** DESCRIPTION */}
                    <div>
                        <p className="px-20 pt-8 text-lg">
                            Enter the name of a state, county, municipality or rural electric
                            cooperative to view its Justice 40 communities, energy communities,
                            and designated low-income census tracts and MSAs on an interactive
                            map. The map will also show a description of available tax credit
                            programs.
                        </p>
                    </div>
                    {/** AUTOCOMPLETE SEARCH BAR */}
                    <div className="px-20 mt-10 mb-5 z-50 self-start w-11/12">
                        <Autocomplete />
                    </div>
                </div>
                {/** REPORT WIDGET */}
                <div>
                    <ReportWidget />
                </div>
            </div>
        </main>
    )
}
