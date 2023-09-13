/**
 * A custom hook to search for geographies by name.
 */

"server only"

import { post } from "@/lib/http";
import { proxy } from "valtio";
import { derive } from "valtio/utils";


function useGeoSearch(initialSearchQuery) {

    /**
     * A private function to search for a geography by name.
     * 
     * @param {*} searchTerm - The search query.
     * @returns A list of the top search reseults.
     */
    const _searchGeographiesByName = async (searchTerm) => {
        if (!searchTerm) return []
        const url = `${process.env.NEXT_PUBLIC_DASHBOARD_BASE_URL}/api/geography/search`;
        const errMsg = `Geography search with query \"${searchTerm}\" failed.`;
        let requestBody = {
            searchTerm: searchTerm,
            limit: parseInt(process.env.NEXT_PUBLIC_NUM_SEARCH_RESULTS)
        };
        return await post(url, requestBody, errMsg);
    };

    // Define state variables
    const state = proxy({
        query: initialSearchQuery,
        selected: null,
        setQuery: (value) => state.query = value,
        setSelected: (value) => state.selected = value
    });

    // Add derived property to state
    derive(
        {
          results: (get) => _searchGeographiesByName(get(state).query).then(r => r),
        },
        {
          proxy: state,
        }
    );

    return [ state ];
}


export { useGeoSearch };