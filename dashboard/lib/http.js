/**
 * HTTP utilities used throughout the application.
 */


/**
 * Makes a POST request and handles any errors that may occur.
 * 
 * @param {*} url - The URL to the resource.
 * @param {*} args - The request body.
 * @param {*} errMsg - A message to display if an error occurs.
 * @returns JSON object
 */
const post = async (url, args, errMsg) => {
    let r = await fetch(url, {
        cache: 'force-cache',
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(args),
    });
    if (!r.ok) {
        return {
            error: errMsg
        };
    }
    return await r.json();
}


/**
 * Makes a GET request and handles any errors that may occur.
 * @param {*} url - The URL to the resource.
 * @param {*} errMsg - A message to display if an error occurs.
 * @returns JSON object.
 */
const get = async (url, errMsg) => {
    let r = await fetch(url, {
        method: "GET",
        headers: { "Content-Type": "application/json" }
    });
    if (!r.ok) {
        return {
            error: errMsg
        };
    };
    let json = await r.json();
    console.log(json.length)
    return json
}

export { get, post };