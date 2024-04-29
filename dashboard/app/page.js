"use client";

/***
 * Renders a widget for searching and viewing tax
 * credit benefit summaries for a geography.
 */

import Autocomplete from "@/components/Autocomplete";
import ReportWidget from "@/components/ReportWidget";

export default function SearchPage() {
  return (
    <div className="max-w-7xl mx-auto py-2 px-2">
      <div className="flex flex-col items-center">
        {/** AUTOCOMPLETE SEARCH BAR */}
        <div className="px-2 sm:px-20 mt-10 mb-5 z-50 self-start w-11/12 mx-auto max-h-[200px]">
          <Autocomplete />
        </div>
      </div>
      {/** REPORT WIDGET */}
      {/* <div className="min-h-[800px]">
        <ReportWidget />
      </div> */}
    </div>
  );
}
